# [C] STIGQter: Arbitrary File Write leading to Local Code Execution via Export HTML

## Summary
Severity: Critical
Advisory: CVE-2026-42881
Aliases: GHSA-mcv5-5j7p-vqh7
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-42881
Type: osv

## Details
STIGQter is an open-source reimplementation of DISA's STIG Viewer. From 0.1.2 to before 1.2.7, an attacker can achieve local code execution (LCE) with the privileges of the user running STIGQter. This requires user interaction: the victim must open the malicious .stigqter file and explicitly run the "Export HTML" action. This vulnerability is fixed in 1.2.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42881.json
- https://github.com/squinky86/STIGQter/security/advisories/GHSA-mcv5-5j7p-vqh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42881
- https://www.bitwizemusic.com/security/advisories/bve-2026-0007
- https://www.bitwizemusic.com/security/advisories/bve-2026-0007/
