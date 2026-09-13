# [M] jq: potential integer overflow in jvp_string_append

## Summary
Severity: Medium
Advisory: CVE-2026-54679
Aliases: GHSA-29gj-222p-j7vx
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54679
Type: osv

## Details
jq is a command-line JSON processor. Prior to 1.8.2, on 32bit system, jvp_string_append has a chance of integer/multiple overflowing and then causing a massive buffer overrun.  This vulnerability is fixed in 1.8.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54679.json
- https://github.com/jqlang/jq/security/advisories/GHSA-29gj-222p-j7vx
- https://nvd.nist.gov/vuln/detail/CVE-2026-54679
