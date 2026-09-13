# [M] JLSEC-2026-1335

## Summary
Severity: Medium
Advisory: JLSEC-2026-1335
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1335
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.81.0+0

## Details
When curl is instructed to download content using the metalink feature, thecontents is verified against a hash provided in the metalink XML file.The metalink XML file points out to the client how to get the same contentfrom a set of different URLs, potentially hosted by different servers and theclient can then download the file from one or several of them. In a serial orparallel manner.If one of the servers hosting the contents has been breached and the contentsof the specific file on that server is replaced with a modified payload, curlshould detect this when the hash of the file mismatches after a completeddownload. It should remove the contents and instead try getting the contentsfrom another URL. This is not done, and instead such a hash mismatch is onlymentioned in text and the potentially malicious content is kept in the file ondisk.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1213175
- https://hackerone.com/reports/1213175
- https://lists.apache.org/thread.html/r61db8e7dcb56dc000a5387a88f7a473bacec5ee01b9ff3f55308aacc%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r61db8e7dcb56dc000a5387a88f7a473bacec5ee01b9ff3f55308aacc%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r61db8e7dcb56dc000a5387a88f7a473bacec5ee01b9ff3f55308aacc%40%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r61db8e7dcb56dc000a5387a88f7a473bacec5ee01b9ff3f55308aacc%40%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cusers.kafka.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRUCW2UVNYUDZF72DQLFQR4PJEC6CF7V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRUCW2UVNYUDZF72DQLFQR4PJEC6CF7V/
- https://security.gentoo.org/glsa/202212-01
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20210902-0003/
- https://security.netapp.com/advisory/ntap-20210902-0003/
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
