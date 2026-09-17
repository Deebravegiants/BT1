# [M] CVE-2021-43099

## Summary
Severity: Medium
Advisory: CVE-2021-43099
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-03-28
Source: https://osv.dev/vulnerability/CVE-2021-43099
Type: osv

## Details
An Archive Extraction (AKA "Zip Slip) vulnerability exists in bbs 5.3 in the UpgradeNow function in UpgradeManageAction.java, which unzips the arbitrary upladed zip file without checking filenames. The vulnerability is exploited using a specially crafted archive that holds directory traversal filenames (e.g. ../../evil.exe).

## References
- https://github.com/diyhi/bbs/issues/51
