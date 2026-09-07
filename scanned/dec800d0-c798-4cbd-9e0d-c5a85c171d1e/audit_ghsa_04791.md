# [M] Statamic Vulnerable to Server-Side Request Forgery via Glide (DNS rebinding)

## Summary
Severity: Medium
Advisory: GHSA-v5c4-wcpj-x73m
CVE: CVE-2026-54242
CWE: CWE-367, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-v5c4-wcpj-x73m
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.24
- Packagist: `statamic/cms` — affected >=6.0.0 <6.20.1

## Details
### Impact

The Glide image proxy's URL validation could be bypassed using DNS rebinding. The remote hostname was validated as publicly routable, but resolved again when the image was actually fetched, so an attacker controlling the hostname's DNS could rebind it to an internal address after validation. This could cause the server to make HTTP requests to internal addresses — including loopback, private network, and cloud metadata endpoints.

This affects sites that pass user-supplied URLs to Glide.


### Patches

This has been fixed in 5.73.24 and 6.20.1.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-v5c4-wcpj-x73m
- https://github.com/statamic/cms
