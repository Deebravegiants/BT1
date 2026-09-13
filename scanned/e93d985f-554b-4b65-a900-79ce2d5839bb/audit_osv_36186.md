# [H] BACnet Stack Improperly Limits Pathnames to a Restricted Directory

## Summary
Severity: High
Advisory: CVE-2026-21878
Aliases: GHSA-p8rx-c26w-545j
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-21878
Type: osv

## Details
BACnet Stack is a BACnet open source protocol stack C library for embedded systems. Prior to 1.5.0.rc3, a vulnerability has been discovered in BACnet Stack's file writing functionality where there is no validation of user-provided file paths, allowing attackers to write files to arbitrary directories. This affects apps/readfile/main.c and ports/posix/bacfile-posix.c. This vulnerability is fixed in 1.5.0.rc3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21878.json
- https://github.com/bacnet-stack/bacnet-stack/security/advisories/GHSA-p8rx-c26w-545j
- https://nvd.nist.gov/vuln/detail/CVE-2026-21878
- https://github.com/bacnet-stack/bacnet-stack/commit/c5dc00a77b4bc2550befa67a930b333e299c18f3
