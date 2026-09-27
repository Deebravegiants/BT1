# [M] Tomahawk authentication timing attack due to usage of 'strcmp'

## Summary
Severity: Medium
Advisory: CVE-2025-57784
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2025-57784
Type: osv

## Details
Tomahawk auth timing attack due to usage of `strcmp` has been identified in Hiawatha webserver version 11.7 which allows a local attacker to access the management client.

## References
- https://gitlab.com/hsleisink/hiawatha/-/blame/master/src/tomahawk.c?ref_type=heads#L429
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57784.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57784
