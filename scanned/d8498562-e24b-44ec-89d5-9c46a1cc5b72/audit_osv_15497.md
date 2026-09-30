# [C] CVE-2019-16868

## Summary
Severity: Critical
Advisory: CVE-2019-16868
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-25
Source: https://osv.dev/vulnerability/CVE-2019-16868
Type: osv

## Details
emlog through 6.0.0beta has an arbitrary file deletion vulnerability via an admin/data.php?action=dell_all_bak request with directory traversal sequences in the bak[] parameter.

## References
- https://github.com/emlog/emlog/issues/48
