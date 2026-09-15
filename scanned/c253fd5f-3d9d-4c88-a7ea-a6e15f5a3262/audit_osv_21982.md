# [H] OFFIS DCMTK Path Traversal

## Summary
Severity: High
Advisory: CVE-2022-2119
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-24
Source: https://osv.dev/vulnerability/CVE-2022-2119
Type: osv

## Details
OFFIS DCMTK's (All versions prior to 3.6.7) service class provider (SCP) is vulnerable to path traversal, allowing an attacker to write DICOM files into arbitrary directories under controlled names. This could allow remote code execution.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00025.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2119.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2119
- https://www.cisa.gov/uscert/ics/advisories/icsma-22-174-01
