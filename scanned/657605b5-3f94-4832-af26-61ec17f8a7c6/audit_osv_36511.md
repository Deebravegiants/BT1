# [M] EVerest vulnerable to concatenation of strings literal and integers

## Summary
Severity: Medium
Advisory: CVE-2026-23955
Aliases: GHSA-px57-jx97-hrff
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2026-23955
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2025.9.0, in several places, integer values are concatenated to literal strings when throwing errors. This results in pointers arithmetic instead of printing the integer value as expected, like most of interpreted languages. This can be used by malicious operator to read unintended memory regions, including the heap and the stack. Version 2025.9.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23955.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-px57-jx97-hrff
- https://nvd.nist.gov/vuln/detail/CVE-2026-23955
