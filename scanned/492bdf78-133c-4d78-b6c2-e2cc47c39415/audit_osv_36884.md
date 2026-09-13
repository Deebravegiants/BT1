# [M] NanaZip has DotNet Single file OOB Heap Read

## Summary
Severity: Medium
Advisory: CVE-2026-26282
Aliases: GHSA-ccpc-2222-xv5c
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-26282
Type: osv

## Details
NanaZip is an open source file archive Starting in version 5.0.1252.0 and prior to version 6.0.1630.0, NanaZip has an out-of-bounds heap read in `.NET Single File` bundle header parser due to missing bounds check. Opening a crafted file with NanaZip causes a crash or leaks heap data to the user. Version 6.0.1630.0 patches the issue.

## References
- https://github.com/user-attachments/files/25274143/poc.exe.zip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26282.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-ccpc-2222-xv5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-26282
