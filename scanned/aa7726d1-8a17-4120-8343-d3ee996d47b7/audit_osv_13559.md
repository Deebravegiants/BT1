# [H] CVE-2018-20332

## Summary
Severity: High
Advisory: CVE-2018-20332
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/CVE-2018-20332
Type: osv

## Details
An issue has been discovered in the OpenWebif plugin through 1.2.4 for Enigma2 based devices. Reading of arbitrary files is possible with /file?action=download&file= followed by a full pathname, and listing of arbitrary directories is possible with /file?action=download&dir= followed by a full pathname. This is related to plugin/controllers/file.py in the e2openplugin-OpenWebif project.

## References
- https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/commit/a846b7664eda3a4c51a452e00638cf7337dc2013
- https://danieltindall.me/openwebif-vulnerabilities
