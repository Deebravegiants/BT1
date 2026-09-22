# [M] jq: stack overflow in module loading on mutual `include`

## Summary
Severity: Medium
Advisory: CVE-2026-44777
Aliases: GHSA-rmpv-jgvr-wpr9
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-44777
Type: osv

## Details
jq is a command-line JSON processor. In 1.8.2rc1 and earlier, the ordinary module loader recurses without cycle detection when two
otherwise valid modules include each other.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44777.json
- https://github.com/jqlang/jq/security/advisories/GHSA-rmpv-jgvr-wpr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44777
