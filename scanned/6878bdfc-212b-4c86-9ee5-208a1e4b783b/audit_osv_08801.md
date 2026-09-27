# [M] CVE-2016-6188

## Summary
Severity: Medium
Advisory: CVE-2016-6188
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/CVE-2016-6188
Type: osv

## Details
Memory leak in SOGo 2.3.7 allows remote attackers to cause a denial of service (memory consumption) via a large number of attempts to upload a large attachment, related to temporary files.

## References
- http://www.openwall.com/lists/oss-security/2016/07/09/3
- http://www.securityfocus.com/bid/96007
- https://sogo.nu/bugs/view.php?id=3510
- https://github.com/inverse-inc/sogo/commit/32bb1456e23a32c7f45079c3985bf732dd0d276d
