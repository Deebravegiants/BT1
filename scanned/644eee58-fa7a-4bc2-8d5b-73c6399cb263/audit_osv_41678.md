# [M] Malcolm has Uncontrolled Resource Consumption in Archive Extraction (Inode-Exhaustion DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-63133
Aliases: GHSA-c35g-mgc3-95rx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-63133
Type: osv

## Details
Malcolm is a network traffic analysis tool suite. Prior to version 26.07.0, `safe-extract.py` extracts uploaded archives with no limit on entry count, directory depth, total entries, or output size. A small malicious archive containing a large number of directory or file entries causes the filebeat processing container to create an unbounded number of filesystem objects, exhausting inodes or filesystem metadata and denying service to the processing pipeline and any service sharing the same mount. Version 26.07.0 fixes the issue.

## References
- https://github.com/cisagov/Malcolm/releases/tag/v26.07.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63133.json
- https://github.com/cisagov/Malcolm/security/advisories/GHSA-c35g-mgc3-95rx
- https://nvd.nist.gov/vuln/detail/CVE-2026-63133
