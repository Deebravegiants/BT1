# [C] Natours has a 1 Click Account take over on reset password via Host Header injection

## Summary
Severity: Critical
Advisory: CVE-2025-53373
Aliases: GHSA-8gmw-7p75-58qv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-53373
Type: osv

## Details
Natours is a Tour Booking API. The attacker can easily take over any victim account by injecting an attacker-controlled server domain in the Host header when requesting the /forgetpassword endpoint. This vulnerability is fixed with commit 7401793a8d9ed0f0c250c4e0ee2815d685d7a70b.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53373.json
- https://github.com/ahmed-elgaml11/Natours/security/advisories/GHSA-8gmw-7p75-58qv
- https://nvd.nist.gov/vuln/detail/CVE-2025-53373
- https://github.com/ahmed-elgaml11/Natours/commit/7401793a8d9ed0f0c250c4e0ee2815d685d7a70b
