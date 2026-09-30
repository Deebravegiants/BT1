# [H] EVerest has off-by-one stack buffer overflow in IsoMux certificate filename parsing

## Summary
Severity: High
Advisory: CVE-2026-22593
Aliases: GHSA-cpqf-mcqc-783m
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-22593
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2026.02.0, an off-by-one check in IsoMux certificate filename handling causes a stack-based buffer overflow when a filename length equals `MAX_FILE_NAME_LENGTH` (100). A crafted filename in the certificate directory can overflow `file_names[idx]`, corrupting stack state and enabling potential code execution. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22593.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-cpqf-mcqc-783m
- https://nvd.nist.gov/vuln/detail/CVE-2026-22593
