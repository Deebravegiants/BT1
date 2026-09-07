# [M] Saloon is vulnerable to SSRF and credential leakage via absolute URL in endpoint overriding base URL

## Summary
Severity: Medium
Advisory: GHSA-c83f-3xp6-hfcp
CVE: CVE-2026-33182
CWE: CWE-522, CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-c83f-3xp6-hfcp
Type: github-advisory

## Affected
- Packagist: `saloonphp/saloon` — affected >=0 <4.0.0

## Details
### Impact
Users providing user generated input into the `resolveEndpoint` method on requests.

### Patches
Upgrade to Saloon v4+

Upgrade guide: https://docs.saloon.dev/upgrade/upgrading-from-v3-to-v4

### Description
When building the request URL, Saloon combined the connector's base URL with the request endpoint. If the endpoint was a valid absolute URL (e.g. https://attacker.example.com/callback), the code used that URL as-is and ignored the base URL. The request—and any authentication headers, cookies, or tokens attached by the connector—was then sent to the attacker-controlled host. If the endpoint could be influenced by user input or configuration (e.g. redirect_uri, callback URL), this allowed server-side request forgery (SSRF) and/or credential leakage to a third-party host. The fix (in the next major version) is to reject absolute URLs in the endpoint: URLHelper::join() throws InvalidArgumentException when the endpoint is a valid absolute URL, unless explicitly allowed, requiring callers to opt-in to the functionality on a per-connector or per-request basis.

### Credits
Saloon thanks @HuajiHD for finding the issue and recommending solutions and @JonPurvis for applying the fix.

## References
- https://github.com/saloonphp/saloon/security/advisories/GHSA-c83f-3xp6-hfcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33182
- https://docs.saloon.dev/upgrade/upgrading-from-v3-to-v4
- https://github.com/saloonphp/saloon
