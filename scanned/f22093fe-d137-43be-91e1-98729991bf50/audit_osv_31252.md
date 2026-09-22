# [H] Arbitrary File Deletion in aimhubio/aim

## Summary
Severity: High
Advisory: CVE-2024-6851
Aliases: GHSA-mrvr-7493-pfq3, PYSEC-2026-1090
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-6851
Type: osv

## Details
In version 3.22.0 of aimhubio/aim, the LocalFileManager._cleanup function in the aim tracking server accepts a user-specified glob-pattern for deleting files. The function does not verify that the matched files are within the directory managed by LocalFileManager, allowing a maliciously crafted glob-pattern to lead to arbitrary file deletion.

## References
- https://huntr.com/bounties/839703fb-23b7-4dc4-ae81-44cd4740d3f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6851.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6851
