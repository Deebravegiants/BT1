# [M] Unauthenticated Reflected XSS via innerHTML in AVideo

## Summary
Severity: Medium
Advisory: GHSA-wfq5-qgqp-hvhv
CVE: CVE-2026-33035
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-wfq5-qgqp-hvhv
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

AVideo contains a reflected XSS vulnerability that allows unauthenticated attackers to execute arbitrary JavaScript in a victim's browser. User input from a URL parameter flows through PHP's `json_encode()` into a JavaScript function that renders it via `innerHTML`, bypassing encoding and achieving full script execution.


## Root Cause
The vulnerability is caused by two issues working together:

### 1. Source: Unescaped user input passed to JavaScript (videoNotFound.php)

**File:** `view/videoNotFound.php` line 49

```php
if (!empty($_REQUEST['404ErrorMsg'])) {
    echo 'avideoAlertInfo(' . json_encode($_REQUEST['404ErrorMsg']) . ');';
}
```

PHP's `json_encode()` with default flags only escapes quotes (`"` → `\"`) and backslashes. It does **NOT** escape HTML special characters (`<`, `>`, `/`). The resulting string contains raw HTML tags that are passed directly to JavaScript.

### 2. Sink: innerHTML renders HTML tags as executable DOM (script.js)

**File:** `view/js/script.js`

```javascript
function avideoAlertInfo(msg) {            // line ~1891
    avideoAlert("", msg, 'info');           // calls ↓
}

function avideoAlert(title, msg, type) {   // line ~1270
    avideoAlertHTMLText(title, msg, type);  // calls ↓
}

function avideoAlertHTMLText(title, msg, type) {  // line ~1451
    var span = document.createElement("span");
    span.innerHTML = msg;                  // line 1464 — XSS SINK
    swal({ content: span });
}
```

`innerHTML` parses the string as HTML. Any `<img>`, `<svg>`, or other HTML tags with event handlers are instantiated as real DOM elements, triggering JavaScript execution.

### Data Flow

```
URL parameter (?404ErrorMsg=PAYLOAD)
    → $_REQUEST['404ErrorMsg']
    → json_encode()          ← does NOT escape < > /
    → avideoAlertInfo()
    → avideoAlert()
    → avideoAlertHTMLText()
    → span.innerHTML = msg   ← renders HTML tags, executes JS
```

---

## Proof of Concept
```
https://localhost/view/videoNotFound.php?404ErrorMsg=<img src=x onerror=alert(document.domain)>
```
<img width="1918" height="1035" alt="image" src="https://github.com/user-attachments/assets/20077ce2-5b49-4bd3-a7df-ab48be786cc1" />

The page renders:
```javascript
avideoAlertInfo("<img src=x onerror=alert(document.domain)>");
```

Which flows to `span.innerHTML = "<img src=x onerror=alert(document.domain)>"`. The browser creates an `<img>` element, `src=x` fails to load, `onerror` fires `alert(document.domain)`.

## Affected Code

| File | Line | Issue |
|------|------|-------|
| `view/videoNotFound.php` | 49 | `json_encode()` does not escape `<` `>` for HTML context |
| `view/js/script.js` | 1464 | `span.innerHTML = msg` renders user input as HTML |
| `view/js/script.js` | 1282 | `span.innerHTML = msg` in `avideoAlertWithCookie()` |
| `view/js/script.js` | 1335 | `span.innerHTML = __(msg,true)` in `avideoConfirm()` |
| `view/js/script.js` | 1358 | `span.innerHTML = msg` in `avideoAlertOnceForceConfirm()` |

The `innerHTML` sink exists in 4 functions. Any future code that passes user input to `avideoAlertInfo()`, `avideoAlertWarning()`, `avideoAlertDanger()`, or `avideoAlertSuccess()` will create additional XSS vectors.


## Remediation

### Fix 1: Escape HTML in PHP (source fix)

```php
// view/videoNotFound.php line 49
// BEFORE (vulnerable):
echo 'avideoAlertInfo(' . json_encode($_REQUEST['404ErrorMsg']) . ');';

// AFTER (fixed):
echo 'avideoAlertInfo(' . json_encode($_REQUEST['404ErrorMsg'], JSON_HEX_TAG | JSON_HEX_AMP) . ');';
```

`JSON_HEX_TAG` converts `<` → `\u003C` and `>` → `\u003E`, preventing HTML injection.

### Fix 2: Use textContent instead of innerHTML (sink fix, recommended)

```javascript
// view/js/script.js - all alert functions
// BEFORE (vulnerable):
span.innerHTML = msg;

// AFTER (fixed):
span.textContent = msg;
```

`textContent` treats the string as plain text — HTML tags are displayed literally, never parsed or executed.

### Fix 3: Add Content-Security-Policy header (defense in depth)

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
```

## Impact

- **Session hijacking** — steal `PHPSESSID` cookie (not HttpOnly by default)
- **Account takeover** — use stolen session to change password or email
- **Phishing** — inject a realistic login form inside the SweetAlert modal
- **Worm propagation** — inject self-spreading payloads via comments/messages
- **Admin compromise** — send crafted link to admin, steal session, gain full control

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-wfq5-qgqp-hvhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33035
- https://github.com/WWBN/AVideo/commit/cca6196f4072cb9acc39b1030fb8fb1702b4f69b
- https://github.com/WWBN/AVideo
