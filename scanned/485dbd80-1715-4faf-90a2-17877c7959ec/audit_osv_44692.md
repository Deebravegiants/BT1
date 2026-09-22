# [M] SiYuan before v3.8.2 Denial of Service via unauthenticated UI-process registration

## Summary
Severity: Medium
Advisory: CVE-2026-85581
Aliases: GHSA-wv96-wmf5-xvj2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85581
Type: osv

## Details
SiYuan before v3.8.2 contains a denial of service vulnerability in the unauthenticated /api/system/uiproc endpoint that accepts and retains attacker-controlled process identifiers without size limits or authentication. Attackers can send repeated requests with unique identifiers to exhaust process memory and degrade service availability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85581.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-wv96-wmf5-xvj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-85581
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-denial-of-service-via-unauthenticated-ui-process-registration
