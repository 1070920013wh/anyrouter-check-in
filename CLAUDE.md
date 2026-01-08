# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation script for multi-account daily check-in on API provider platforms (AnyRouter, AgentRouter, and any NewAPI/OneAPI compatible services). The script runs on GitHub Actions every 6 hours and supports 8 notification platforms.

**Key Technologies**: Python 3.11+, asyncio, Playwright (headless browser for WAF bypass), httpx (HTTP/2 client)

## Development Commands

```bash
# Install all dependencies (including dev tools)
uv sync --dev

# Install Playwright browser for WAF bypass
uv run playwright install chromium

# Run the check-in script locally
uv run checkin.py

# Run tests
uv run pytest tests/

# Run tests with coverage
uv run pytest --cov=utils tests/

# Run linter and formatter (Ruff)
uv run ruff check .
uv run ruff format .

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

## Architecture

The project follows a modular architecture with clear separation of concerns:

```
checkin.py (Entry Point)
    ├── Configuration Layer (utils/config.py)
    │   ├── AppConfig: Loads provider configurations from env
    │   ├── ProviderConfig: Individual provider settings (domain, paths, bypass method)
    │   └── AccountConfig: User account configurations
    │
    ├── Business Logic (checkin.py)
    │   ├── WAF Cookie Management (Playwright browser automation)
    │   ├── User Info Retrieval (HTTP requests)
    │   └── Check-in Execution (HTTP POST requests)
    │
    └── Notification Layer (utils/notify.py)
        └── NotificationKit: Multi-platform notification system
```

### Workflow Overview

1. **Configuration Loading**: `AppConfig.load_from_env()` loads built-in providers (anyrouter, agentrouter) and merges with custom `PROVIDERS` env var
2. **Account Processing**: For each account:
   - Check if WAF bypass is needed (`provider.needs_waf_cookies()`)
   - If needed, launch headless Chromium via Playwright to obtain WAF cookies
   - Merge WAF cookies with user session cookies
   - Fetch user info (balance/quota)
   - Execute check-in if required (`provider.needs_manual_check_in()`)
3. **Notification Decision**: Only notify if:
   - Any account fails OR
   - Balance changes detected (via SHA256 hash comparison)
4. **Exit**: Exit code 0 if any account succeeds, 1 if all fail

### Key Files

- `checkin.py:266` - `main()`: Async orchestration
- `checkin.py:205` - `check_in_account()`: Single account logic
- `checkin.py:68` - `get_waf_cookies_with_playwright()`: Browser automation for WAF bypass
- `utils/config.py:76` - `AppConfig.load_from_env()`: Provider configuration loading
- `utils/config.py:42` - `ProviderConfig.from_dict()`: Custom provider parsing
- `utils/notify.py:123` - `NotificationKit.push_message()`: Broadcast notifications

## Provider Configuration

### Built-in Providers

- **anyrouter**: Requires WAF bypass (`bypass_method: "waf_cookies"`), manual check-in required
- **agentrouter**: Requires WAF bypass, check-in happens automatically on user info request

### Custom Providers

Use `PROVIDERS` env var (JSON). Custom configs override built-in ones with same name:

```json
{
  "customrouter": {
    "domain": "https://custom.example.com",
    "login_path": "/login",
    "sign_in_path": "/api/user/sign_in",
    "user_info_path": "/api/user/self",
    "api_user_key": "new-api-user",
    "bypass_method": "waf_cookies",
    "waf_cookie_names": ["acw_tc", "cdn_sec_tc"]
  }
}
```

**Important**:
- `bypass_method: "waf_cookies"` - Use Playwright to get WAF cookies, then manual check-in
- `bypass_method: null` or unset - Direct requests (no WAF), check-in via sign_in_path
- `sign_in_path: null` - Check-in happens automatically (like agentrouter)

## WAF Bypass Strategy

For providers with `bypass_method: "waf_cookies"`:

1. Launch ephemeral Chromium context via Playwright
2. Navigate to login page to acquire WAF cookies
3. Extract specific cookies (e.g., `acw_tc`, `cdn_sec_tc`, `acw_sc__v2`)
4. Merge with user session cookies for subsequent requests

See `checkin.py:68` for implementation.

## Balance Change Detection

- Hashes balance data (SHA256, truncated to 16 chars)
- Stores hash in `balance_hash.txt`
- Compares current vs previous hash to detect changes
- Triggers notification on first run or balance changes

See `checkin.py:45` for `generate_balance_hash()`.

## Code Style

- **Indentation**: Tabs
- **Line length**: 120 characters
- **Quotes**: Single quotes
- **Linter**: Ruff (ASYNC, E, F, FAST, I, PLE rules)
- **Pre-commit hooks**: Enforce trailing whitespace, YAML/JSON/TOML validation, large file detection, Ruff

## Testing

- Unit tests in `tests/test_notify.py` use pytest + mocks
- Real API test available via `ENABLE_REAL_TEST=true` env var
- Tests are mock-based by default for CI/CD efficiency

## Environment Variables

**Required**:
- `ANYROUTER_ACCOUNTS` - JSON array of account configs

**Optional**:
- `PROVIDERS` - Custom provider configs (JSON)
- Notification platform configs (EMAIL_USER, DINGDING_WEBHOOK, etc.)

## Common Patterns

- **Async functions**: Use `async def` and `await` for I/O operations
- **Error handling**: Partial success allowed - track failures but continue processing
- **Logging**: Use structured prefixes `[INFO]`, `[SUCCESS]`, `[FAILED]`, `[PROCESSING]`, `[NETWORK]`, `[RESPONSE]`, `[NOTIFY]`
- **Type hints**: Use `dict | None` syntax (Python 3.11+)
