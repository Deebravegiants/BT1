# [H] CVE-2026-37230

## Summary
Severity: High
Advisory: CVE-2026-37230
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37230
Type: osv

## Details
FlexRIC v2.0.0 crashes when the near-RT RIC receives a RIC_INDICATION message with a ran_func_id that does not exist in its registry. The lookup returns NULL, triggering assert() in Debug builds (SIGABRT) or NULL pointer dereference in Release builds (SIGSEGV). A remote unauthenticated attacker can crash the near-RT RIC (port 36421) by sending a crafted RIC_INDICATION with an arbitrary ran_func_id value.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37230.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37230.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37230
- https://gitlab.eurecom.fr/mosaic5g/flexric
