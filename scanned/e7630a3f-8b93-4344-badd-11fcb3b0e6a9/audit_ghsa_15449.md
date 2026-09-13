# [M] Bostr Improper Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5cf7-cxrf-mq73
CVE: CVE-2024-41962
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-08-02
Source: https://github.com/advisories/GHSA-5cf7-cxrf-mq73
Type: github-advisory

## Affected
- npm: `bostr` — affected >=0 <3.0.10

## Details
Even with `authorized_keys` is filled with allowed pubkeys, If `noscraper` is enabled, It will allow anyone to use bouncer even it's pubkey is not in `authorized_keys`.

### Impact
- Private bouncer

### Patches
Available on version [3.0.10](https://github.com/Yonle/bostr/releases/tag/3.0.10)

### Workarounds
Disable `noscraper` if you have `authorized_keys` being set in config

### References
This [line of code](https://github.com/Yonle/bostr/blob/8665374a66e2afb9f92d0414b0d6f420a95d5d2d/auth.js#L21) is the cause.

## References
- https://github.com/Yonle/bostr/security/advisories/GHSA-5cf7-cxrf-mq73
- https://nvd.nist.gov/vuln/detail/CVE-2024-41962
- https://github.com/Yonle/bostr/commit/49181f4ec9ae1472c6675cab56bbc01e723855af
- https://github.com/Yonle/bostr
- https://github.com/Yonle/bostr/blob/8665374a66e2afb9f92d0414b0d6f420a95d5d2d/auth.js#L21
- https://github.com/Yonle/bostr/releases/tag/3.0.10
