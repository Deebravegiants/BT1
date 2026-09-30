# [C] CVE-2018-11248

## Summary
Severity: Critical
Advisory: CVE-2018-11248
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-11248
Type: osv

## Details
util/FileDownloadUtils.java in FileDownloader 1.7.3 does not check an attachment's name. If an attacker places "../" in the file name, the file can be stored in an unintended directory because of Directory Traversal.

## References
- https://github.com/lingochamp/FileDownloader/issues/1028
