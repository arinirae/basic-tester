from __future__ import annotations

import asyncio
import json
import logging
import os
import platform
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Page

# Fix for Windows + Python 3.13 compatibility
if platform.system() == "Windows":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except AttributeError:
        # Fallback for older Python versions
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BROWSER_LAUNCH_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-web-security',
    '--disable-background-networking',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-breakpad',
    '--disable-client-side-phishing-detection',
    '--disable-default-apps',
    '--disable-extensions',
    '--disable-features=IsolateOrigins,site-per-process',
    '--disable-hang-monitor',
    '--disable-popup-blocking',
    '--disable-prompt-on-repost',
    '--disable-sync',
    '--metrics-recording-only',
    '--mute-audio',
    '--no-first-run',
    '--no-zygote',
    '--safebrowsing-disable-auto-update',
    '--window-size=1280,800',
]

# Global flag to track if we should use sync mode
USE_SYNC_MODE = False


def _handle_login_for_test_sync(page, login_config: Dict[str, Any]) -> None:
    """Handle login process for test execution (sync version)"""
    logger.info("Handling login process for test execution (sync)...")
    
    login_url = login_config.get("login_url")
    if not login_url:
        logger.warning("No login URL provided for test execution")
        return
        
    username_field = login_config.get("login_username_field")
    email_field = login_config.get("login_email_field") 
    password_field = login_config.get("login_password_field")
    username = login_config.get("login_username")
    email = login_config.get("login_email")
    password = login_config.get("login_password")
    
    if not (((username_field and username) or (email_field and email)) and password_field and password):
        logger.warning("Incomplete login credentials for test execution")
        return
    
    # Navigate to login page
    logger.info(f"Navigating to login URL: {login_url}")
    page.goto(login_url, wait_until='domcontentloaded', timeout=90000)
    page.wait_for_timeout(3000)
    
    # Fill login credentials
    if username_field and username:
        try:
            page.fill(f'input[name="{username_field}"]', username)
            logger.info(f"Filled username field: {username_field}")
        except Exception as e:
            logger.warning(f"Could not fill username field {username_field}: {e}")
    
    if email_field and email:
        try:
            page.fill(f'input[name="{email_field}"]', email)
            logger.info(f"Filled email field: {email_field}")
        except Exception as e:
            logger.warning(f"Could not fill email field {email_field}: {e}")
    
    if password_field and password:
        try:
            page.fill(f'input[name="{password_field}"]', password)
            logger.info(f"Filled password field: {password_field}")
        except Exception as e:
            logger.warning(f"Could not fill password field {password_field}: {e}")
    
    # Try to submit the login form with improved button detection
    try:
        # Look for submit button and click it
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'input[type="button"]',
            'button[class*="btnLogin"]',
            'button[id*="btnLogOn"]',
            'button[id*="btnLog"]',
            'input[id*="btnSave"]',
            'button:contains("Login")',
            'button:contains("Sign In")',
            'button:contains("Log In")',
            'input[value*="login" i]',
            'input[value*="sign in" i]',
            'input[value*="log in" i]',
            'button[class*="login"]',
            'button[class*="signin"]',
            'input[class*="login"]',
            'input[class*="signin"]'
        ]
        
        submit_clicked = False
        for selector in submit_selectors:
            try:
                if selector.startswith('button:contains') or selector.startswith('input[value*='):
                    # Handle text-based selectors
                    if selector.startswith('button:contains'):
                        text = selector.split('"')[1]
                        page.click(f'button:has-text("{text}")', timeout=5000)
                    else:
                        value_pattern = selector.split('"')[1]
                        page.click(f'input[value*="{value_pattern}" i]', timeout=5000)
                else:
                    page.click(selector, timeout=5000)
                submit_clicked = True
                logger.info(f"Clicked login submit button with selector: {selector}")
                break
            except:
                continue
        
        if submit_clicked:
            # Wait for navigation or page change after login
            page.wait_for_timeout(5000)
            
            # Try to detect if login was successful by checking if we're still on login page
            current_url = page.url
            if login_url in current_url or "login" in current_url.lower():
                logger.warning("Login may have failed - still on login page")
                # Try alternative submission method
                try:
                    page.evaluate("() => document.querySelector('form')?.submit()")
                    page.wait_for_timeout(3000)
                    logger.info("Tried form.submit() as fallback")
                except Exception as e:
                    logger.warning(f"Form submit fallback failed: {e}")
            else:
                logger.info("Login appears successful - navigated away from login page")
        else:
            logger.warning("Could not find login submit button, trying form.submit()")
            try:
                page.evaluate("() => document.querySelector('form')?.submit()")
                page.wait_for_timeout(3000)
            except Exception as e:
                logger.warning(f"Form submit failed: {e}")
                
    except Exception as e:
        logger.warning(f"Login submission failed: {e}")


def _handle_login_sync(page, login_config: Dict[str, Any]) -> None:
    """Handle login process before field detection (sync version)"""
    logger.info("Handling login process (sync)...")
    
    login_url = login_config.get("login_url")
    if login_url and login_url != page.url:
        logger.info(f"Navigating to login URL: {login_url}")
        page.goto(login_url, wait_until='domcontentloaded', timeout=90000)
        page.wait_for_timeout(2000)
    
    # Fill login credentials
    login_fields = []
    
    # Handle username field
    username_field = login_config.get("login_username_field")
    username_value = login_config.get("login_username")
    if username_field and username_value:
        login_fields.append((username_field, username_value))
    
    # Handle email field  
    email_field = login_config.get("login_email_field")
    email_value = login_config.get("login_email")
    if email_field and email_value:
        login_fields.append((email_field, email_value))
    
    # Handle password field
    password_field = login_config.get("login_password_field")
    password_value = login_config.get("login_password")
    if password_field and password_value:
        login_fields.append((password_field, password_value))
    
    # Fill the fields
    for field_name, field_value in login_fields:
        try:
            selector = f'input[name="{field_name}"]'
            page.fill(selector, field_value)
            logger.info(f"Filled {field_name} field (sync)")
        except Exception as e:
            logger.warning(f"Could not fill {field_name} field (sync): {e}")
    
    # Try to submit the login form
    try:
        # Look for submit button and click it
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'input[type="button"]',
            'button[class*="btnLogin"]',
            'button[id*="btnLogOn"]',
            'button[id*="btnLog"]',
            'input[id*="btnSave"]',
            'button:contains("Login")',
            'button:contains("Sign In")',
            'button:contains("Log In")',
            'input[value*="login" i]',
            'input[value*="sign in" i]',
            'input[value*="log in" i]',
            'button[class*="login"]',
            'button[class*="signin"]',
            'input[class*="login"]',
            'input[class*="signin"]'
        ]
        
        submit_clicked = False
        for selector in submit_selectors:
            try:
                if selector.startswith('button:contains') or selector.startswith('input[value*='):
                    # Handle text-based selectors
                    if selector.startswith('button:contains'):
                        text = selector.split('"')[1]
                        page.click(f'button:has-text("{text}")', timeout=5000)
                    else:
                        value_pattern = selector.split('"')[1]
                        page.click(f'input[value*="{value_pattern}" i]', timeout=5000)
                else:
                    page.click(selector, timeout=5000)
                submit_clicked = True
                logger.info("Clicked login submit button (sync)")
                break
            except:
                continue
        
        if submit_clicked:
            # Wait for navigation or page change
            page.wait_for_timeout(5000)
            logger.info("Login process completed (sync)")
        else:
            logger.warning("Could not find login submit button (sync)")
            
    except Exception as e:
        logger.warning(f"Login submission failed (sync): {e}")


def detect_form_fields_sync(url: str, login_config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Synchronous fallback for form field detection"""
    from playwright.sync_api import sync_playwright

    logger.info(f"Starting sync form field detection for URL: {url}")
    try:
        with sync_playwright() as p:
            logger.info("Launching browser (sync)...")
            browser = p.chromium.launch(headless=True, args=BROWSER_LAUNCH_ARGS, timeout=60000)
            logger.info("Creating new page (sync)...")
            page = browser.new_page(
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
            )
            logger.info(f"Navigating to {url} (sync)...")
            page.goto(url, wait_until='domcontentloaded', timeout=90000)
            
            # Handle login if required
            if login_config:
                _handle_login_sync(page, login_config)
            
            page.wait_for_timeout(3000)
            try:
                logger.info("Waiting for form elements (sync)...")
                page.wait_for_selector('input, textarea, select', timeout=15000)
            except Exception as e:
                logger.warning(f"Timeout waiting for form elements: {e}")

            logger.info("Evaluating form fields (sync)...")
            fields = page.evaluate(
                """
                () => {
                    return Array.from(document.querySelectorAll(
                        'input:not([type=hidden]):not([type=submit]):not([type=button]), textarea, select'
                    )).map(el => ({
                        name: el.name || el.id || '',
                        label: el.labels?.[0]?.textContent?.trim() || (el.placeholder || el.name || el.id || ''),
                        type: el.type || el.tagName.toLowerCase(),
                        required: el.required || false,
                        placeholder: el.placeholder || '',
                        options: el.tagName.toLowerCase() === 'select'
                            ? Array.from(el.options).map(o => o.value || o.textContent || '')
                            : []
                    })).filter(field => field.name !== '');
                }
                """
            )
            logger.info(f"Found {len(fields)} form fields (sync)")
            browser.close()
            return fields
    except Exception as e:
        logger.error(f"Error in sync form field detection: {e}")
        raise


ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "test_results"
RESULTS_DIR.mkdir(exist_ok=True)


async def _handle_login_for_test(page: Page, login_config: Dict[str, Any]) -> None:
    """Handle login process for test execution - login first, then navigate to target URL"""
    logger.info("Handling login process for test execution...")
    
    login_url = login_config.get("login_url")
    if not login_url:
        logger.warning("No login URL provided for test execution")
        return
        
    username_field = login_config.get("login_username_field")
    email_field = login_config.get("login_email_field") 
    password_field = login_config.get("login_password_field")
    username = login_config.get("login_username")
    email = login_config.get("login_email")
    password = login_config.get("login_password")
    
    if not (((username_field and username) or (email_field and email)) and password_field and password):
        logger.warning("Incomplete login credentials for test execution")
        return
    
    # Navigate to login page
    logger.info(f"Navigating to login URL: {login_url}")
    await page.goto(login_url, wait_until='domcontentloaded', timeout=90000)
    await page.wait_for_timeout(3000)
    
    # Fill login credentials
    if username_field and username:
        try:
            await page.fill(f'input[name="{username_field}"]', username)
            logger.info(f"Filled username field: {username_field}")
        except Exception as e:
            logger.warning(f"Could not fill username field {username_field}: {e}")
    
    if email_field and email:
        try:
            await page.fill(f'input[name="{email_field}"]', email)
            logger.info(f"Filled email field: {email_field}")
        except Exception as e:
            logger.warning(f"Could not fill email field {email_field}: {e}")
    
    if password_field and password:
        try:
            await page.fill(f'input[name="{password_field}"]', password)
            logger.info(f"Filled password field: {password_field}")
        except Exception as e:
            logger.warning(f"Could not fill password field {password_field}: {e}")
    
    # Try to submit the login form with improved button detection
    try:
        # Look for submit button and click it
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'input[type="button"]',
            'button[class*="btnLogin"]',
            'button[id*="btnLogOn"]',
            'button[id*="btnLog"]',
            'input[id*="btnSave"]',
            'button:contains("Login")',
            'button:contains("Sign In")',
            'button:contains("Log In")',
            'input[value*="login" i]',
            'input[value*="sign in" i]',
            'input[value*="log in" i]',
            'button[class*="login"]',
            'button[class*="signin"]',
            'input[class*="login"]',
            'input[class*="signin"]'
        ]
        
        submit_clicked = False
        for selector in submit_selectors:
            try:
                if selector.startswith('button:contains') or selector.startswith('input[value*='):
                    # Handle text-based selectors
                    if selector.startswith('button:contains'):
                        text = selector.split('"')[1]
                        await page.click(f'button:has-text("{text}")', timeout=5000)
                    else:
                        value_pattern = selector.split('"')[1]
                        await page.click(f'input[value*="{value_pattern}" i]', timeout=5000)
                else:
                    await page.click(selector, timeout=5000)
                submit_clicked = True
                logger.info(f"Clicked login submit button with selector: {selector}")
                break
            except:
                continue
        
        if submit_clicked:
            # Wait for navigation or page change after login
            await page.wait_for_timeout(5000)
            
            # Try to detect if login was successful by checking if we're still on login page
            current_url = page.url
            if login_url in current_url or "login" in current_url.lower():
                logger.warning("Login may have failed - still on login page")
                # Try alternative submission method
                try:
                    await page.evaluate("() => document.querySelector('form')?.submit()")
                    await page.wait_for_timeout(3000)
                    logger.info("Tried form.submit() as fallback")
                except Exception as e:
                    logger.warning(f"Form submit fallback failed: {e}")
            else:
                logger.info("Login appears successful - navigated away from login page")
        else:
            logger.warning("Could not find login submit button, trying form.submit()")
            try:
                await page.evaluate("() => document.querySelector('form')?.submit()")
                await page.wait_for_timeout(3000)
            except Exception as e:
                logger.warning(f"Form submit failed: {e}")
                
    except Exception as e:
        logger.warning(f"Login submission failed: {e}")


async def _handle_login(page: Page, login_config: Dict[str, Any]) -> None:
    """Handle login process before field detection"""
    logger.info("Handling login process...")
    
    login_url = login_config.get("login_url")
    if login_url and login_url != page.url:
        logger.info(f"Navigating to login URL: {login_url}")
        await page.goto(login_url, wait_until='domcontentloaded', timeout=90000)
        await page.wait_for_timeout(2000)
    
    # Fill login credentials
    login_fields = []
    
    # Handle username field
    username_field = login_config.get("login_username_field")
    username_value = login_config.get("login_username")
    if username_field and username_value:
        login_fields.append((username_field, username_value))
    
    # Handle email field  
    email_field = login_config.get("login_email_field")
    email_value = login_config.get("login_email")
    if email_field and email_value:
        login_fields.append((email_field, email_value))
    
    # Handle password field
    password_field = login_config.get("login_password_field")
    password_value = login_config.get("login_password")
    if password_field and password_value:
        login_fields.append((password_field, password_value))
    
    # Fill the fields
    for field_name, field_value in login_fields:
        try:
            selector = f'input[name="{field_name}"]'
            await page.fill(selector, field_value)
            logger.info(f"Filled {field_name} field")
        except Exception as e:
            logger.warning(f"Could not fill {field_name} field: {e}")
    
    # Try to submit the login form
    try:
        # Look for submit button and click it
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'input[type="button"]',
            'button[class*="btnLogin"]',
            'button[id*="btnLogOn"]',
            'button[id*="btnLog"]',
            'input[id*="btnSave"]',
            'button:contains("Login")',
            'button:contains("Sign In")',
            'button:contains("Log In")',
            'input[value*="login" i]',
            'input[value*="sign in" i]',
            'input[value*="log in" i]',
            'button[class*="login"]',
            'button[class*="signin"]',
            'input[class*="login"]',
            'input[class*="signin"]'
        ]
        
        submit_clicked = False
        for selector in submit_selectors:
            try:
                if selector.startswith('button:contains') or selector.startswith('input[value*='):
                    # Handle text-based selectors
                    if selector.startswith('button:contains'):
                        text = selector.split('"')[1]
                        await page.click(f'button:has-text("{text}")', timeout=5000)
                    else:
                        value_pattern = selector.split('"')[1]
                        await page.click(f'input[value*="{value_pattern}" i]', timeout=5000)
                else:
                    await page.click(selector, timeout=5000)
                submit_clicked = True
                logger.info("Clicked login submit button")
                break
            except:
                continue
        
        if submit_clicked:
            # Wait for navigation or page change
            await page.wait_for_timeout(5000)
            logger.info("Login process completed")
        else:
            logger.warning("Could not find login submit button")
            
    except Exception as e:
        logger.warning(f"Login submission failed: {e}")


async def detect_form_fields(url: str, login_config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    logger.info(f"Starting form field detection for URL: {url}")
    try:
        async with async_playwright() as p:
            logger.info("Launching browser...")
            browser = await p.chromium.launch(headless=True, args=BROWSER_LAUNCH_ARGS, timeout=60000)
            logger.info("Creating new page...")
            page = await browser.new_page(
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
            )
            logger.info(f"Navigating to {url}...")
            await page.goto(url, wait_until='domcontentloaded', timeout=90000)
            
            # Handle login if required
            if login_config:
                await _handle_login(page, login_config)
            
            await page.wait_for_timeout(3000)
            try:
                logger.info("Waiting for form elements...")
                await page.wait_for_selector('input, textarea, select', timeout=15000)
            except Exception as e:
                logger.warning(f"Timeout waiting for form elements: {e}")

            logger.info("Evaluating form fields...")
            fields = await page.evaluate(
                """
                () => {
                    return Array.from(document.querySelectorAll(
                        'input:not([type=hidden]):not([type=submit]):not([type=button]), textarea, select'
                    )).map(el => ({
                        name: el.name || el.id || '',
                        label: el.labels?.[0]?.textContent?.trim() || (el.placeholder || el.name || el.id || ''),
                        type: el.type || el.tagName.toLowerCase(),
                        required: el.required || false,
                        placeholder: el.placeholder || '',
                        options: el.tagName.toLowerCase() === 'select'
                            ? Array.from(el.options).map(o => o.value || o.textContent || '')
                            : []
                    })).filter(field => field.name !== '');
                }
                """
            )
            logger.info(f"Found {len(fields)} form fields")
            await browser.close()
            return fields
    except Exception as e:
        logger.warning(f"Async mode failed, trying sync mode: {e}")
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, detect_form_fields_sync, url, login_config)
        except Exception as sync_e:
            logger.error(f"Both async and sync modes failed. Async error: {e}, Sync error: {sync_e}")
            raise sync_e


async def _fill_field(page: Page, field: Dict[str, Any], value: Any) -> None:
    selector = f'input[name="{field.get("name")}"]'
    field_type = str(field.get("type", "text")).lower()
    if field_type == "checkbox":
        if value:
            await page.check(selector)
        else:
            await page.uncheck(selector)
        return

    if field_type == "select":
        await page.select_option(selector, str(value))
        return

    if field_type in ["radio"]:
        await page.check(f'input[name="{field.get("name")}"][value="{value}"]')
        return

    await page.fill(selector, str(value or ""))


def run_test_scenario_sync(
    target_url: str,
    values: Dict[str, Any],
    scenario_id: int,
    login_config: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Synchronous fallback for test scenario execution"""
    from playwright.sync_api import sync_playwright

    start_time = time.perf_counter()
    logger.info(f"Starting sync test scenario execution for scenario {scenario_id}")
    try:
        with sync_playwright() as p:
            logger.info("Launching browser (sync)...")
            browser = p.chromium.launch(headless=True, args=BROWSER_LAUNCH_ARGS, timeout=60000)
            logger.info("Creating new page (sync)...")
            page = browser.new_page(
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
            )

            if login_config:
                _handle_login_for_test_sync(page, login_config)

            logger.info(f"Navigating to target URL: {target_url} (sync)")
            page.goto(target_url, wait_until='domcontentloaded', timeout=90000)

            for name, value in values.items():
                field = {"name": name, "type": "text"}
                if isinstance(value, bool):
                    field["type"] = "checkbox"
                elif isinstance(value, int):
                    field["type"] = "number"
                _fill_field_sync(page, field, value)

            # Take screenshot after filling fields but before submitting
            filled_screenshot_path = RESULTS_DIR / f"scenario_{scenario_id}_filled_{int(time.time())}.png"
            page.screenshot(path=str(filled_screenshot_path), full_page=True)
            logger.info(f"Taken screenshot after filling fields: {filled_screenshot_path.name}")

            try:
                page.click('button[type="submit"], input[type="submit"]')
            except Exception:
                page.evaluate("() => document.querySelector('form')?.submit()")

            page.wait_for_timeout(1500)
            # Take screenshot after submitting
            submitted_screenshot_path = RESULTS_DIR / f"scenario_{scenario_id}_submitted_{int(time.time())}.png"
            page.screenshot(path=str(submitted_screenshot_path), full_page=True)
            logger.info(f"Taken screenshot after submitting: {submitted_screenshot_path.name}")
            browser.close()

        duration = time.perf_counter() - start_time
        logger.info(f"Sync test scenario completed in {duration:.2f} seconds")
        return {
            "status": "passed",
            "duration": round(duration, 2),
            "filled_screenshot": str(filled_screenshot_path.name),
            "submitted_screenshot": str(submitted_screenshot_path.name),
        }
    except Exception as e:
        logger.error(f"Error in sync test scenario execution: {e}")
        raise


def _fill_field_sync(page, field: Dict[str, Any], value: Any) -> None:
    """Sync version of _fill_field"""
    selector = f'input[name="{field.get("name")}"]'
    field_type = str(field.get("type", "text")).lower()
    if field_type == "checkbox":
        if value:
            page.check(selector)
        else:
            page.uncheck(selector)
        return

    if field_type == "select":
        page.select_option(selector, str(value))
        return

    if field_type in ["radio"]:
        page.check(f'input[name="{field.get("name")}"][value="{value}"]')
        return

    page.fill(selector, str(value or ""))


async def run_test_scenario(
    target_url: str,
    values: Dict[str, Any],
    scenario_id: int,
    login_config: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    start_time = time.perf_counter()
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=BROWSER_LAUNCH_ARGS, timeout=60000)
            page = await browser.new_page(
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
            )

            if login_config:
                await _handle_login_for_test(page, login_config)

            await page.goto(target_url, wait_until='domcontentloaded', timeout=90000)
            await page.wait_for_timeout(3000)

            for name, value in values.items():
                field = {"name": name, "type": "text"}
                if isinstance(value, bool):
                    field["type"] = "checkbox"
                elif isinstance(value, int):
                    field["type"] = "number"
                await _fill_field(page, field, value)

            # Take screenshot after filling fields but before submitting
            filled_screenshot_path = RESULTS_DIR / f"scenario_{scenario_id}_filled_{int(time.time())}.png"
            await page.screenshot(path=str(filled_screenshot_path), full_page=True)
            logger.info(f"Taken screenshot after filling fields: {filled_screenshot_path.name}")

            try:
                await page.click('button[type="submit"], input[type="submit"]')
            except Exception:
                await page.evaluate("() => document.querySelector('form')?.submit()")

            await page.wait_for_timeout(1500)
            # Take screenshot after submitting
            submitted_screenshot_path = RESULTS_DIR / f"scenario_{scenario_id}_submitted_{int(time.time())}.png"
            await page.screenshot(path=str(submitted_screenshot_path), full_page=True)
            logger.info(f"Taken screenshot after submitting: {submitted_screenshot_path.name}")
            await browser.close()

        duration = time.perf_counter() - start_time
        return {
            "status": "passed",
            "duration": round(duration, 2),
            "filled_screenshot": str(filled_screenshot_path.name),
            "submitted_screenshot": str(submitted_screenshot_path.name),
        }
    except Exception as e:
        logger.warning(f"Async mode failed for run_test_scenario, trying sync mode: {e}")
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, run_test_scenario_sync, target_url, values, scenario_id, login_config)
        except Exception as sync_e:
            logger.error(f"Both async and sync modes failed for run_test_scenario. Async error: {e}, Sync error: {sync_e}")
            raise sync_e
