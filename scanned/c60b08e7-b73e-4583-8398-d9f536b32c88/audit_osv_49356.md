# [M] CVE-2019-11070

## Summary
Severity: Medium
Advisory: CVE-2019-11070
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-04-10
Source: https://osv.dev/vulnerability/CVE-2019-11070
Type: osv

## Details
WebKitGTK and WPE WebKit prior to version 2.24.1 failed to properly apply configured HTTP proxy settings when downloading livestream video (HLS, DASH, or Smooth Streaming), an error resulting in deanonymization. This issue was corrected by changing the way livestreams are downloaded.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00025.html
- https://usn.ubuntu.com/3948-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00031.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YO5ZBUWOOXMVZPBYLZRDZF6ZQGBYJERQ/
- http://www.openwall.com/lists/oss-security/2019/04/11/1
- https://seclists.org/bugtraq/2019/Apr/21
- https://security.gentoo.org/glsa/201909-05
- http://packetstormsecurity.com/files/152485/WebKitGTK-WPE-WebKit-URI-Spoofing-Code-Execution.html
- https://bugs.webkit.org/show_bug.cgi?id=193718
- https://trac.webkit.org/changeset/243197/webkit
