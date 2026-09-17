# [H] PYSEC-2023-291

## Summary
Severity: High
Advisory: PYSEC-2023-291
Aliases: CVE-2023-49297, GHSA-v5f6-hjmf-9mc5
Ecosystem: PyPI
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-05
Source: https://osv.dev/vulnerability/PYSEC-2023-291
Type: osv

## Affected
- PyPI: `pydrive2` — affected >=0 <c57355dc2033ad90b7050d681b2c3ba548ff0004, >=0 <1.16.2

## Details
PyDrive2 is a wrapper library of google-api-python-client that simplifies many common Google Drive API V2 tasks. Unsafe YAML deserilization will result in arbitrary code execution. A maliciously crafted YAML file can cause arbitrary code execution if PyDrive2 is run in the same directory as it, or if it is loaded in via `LoadSettingsFile`. This is a deserilization attack that will affect any user who initializes GoogleAuth from this package while a malicious yaml file is present in the same directory. This vulnerability does not require the file to be directly loaded through the code, only present. This issue has been addressed in commit `c57355dc` which is included in release version `1.16.2`. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/iterative/PyDrive2/security/advisories/GHSA-v5f6-hjmf-9mc5
- https://github.com/iterative/PyDrive2/commit/c57355dc2033ad90b7050d681b2c3ba548ff0004
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CYR5SJKOFSSXFV3E3D2SLXBUBA5WMJJG/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/K34YWTDKBAYWZPOAKBYDM72WIFL5CAYW/
