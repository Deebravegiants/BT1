# [M] AVideo CVE-2026-43884 incomplete fix - six (or more) `isSSRFSafeURL()` call sites still discard the `$resolvedIP` out-param at master HEAD post-`603e7bf`

## Summary
Severity: Medium
Advisory: GHSA-c3ch-22rq-xfwr
CVE: CVE-2026-45619
CWE: CWE-367, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-c3ch-22rq-xfwr
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
CVE-2026-43884 fix `603e7bf` patched `EpgParser.php` and `plugin/AI/receiveAsync.json.php` to use `url_get_contents` (redirect-safe). Neither uses the `$resolvedIP` out-param of `isSSRFSafeURL()` for DNS pinning via `CURLOPT_RESOLVE`. Six+ other call sites still discard `$resolvedIP`, opening DNS-rebinding TOCTOU.

Reference correct pattern at `plugin/YPTWallet/YPTWallet.php:1071-1098`:

```php
$resolvedIP = null;
if (isSSRFSafeURL($url, $resolvedIP)) {
    curl_setopt($ch, CURLOPT_RESOLVE, ["$h

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-c3ch-22rq-xfwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45619
- https://github.com/WWBN/AVideo
- https://github.com/advisories/GHSA-2hch-c97c-g99x
