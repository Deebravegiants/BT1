# [H] CVE-2018-16874

## Summary
Severity: High
Advisory: CVE-2018-16874
Aliases: GO-2022-0190
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-14
Source: https://osv.dev/vulnerability/CVE-2018-16874
Type: osv

## Details
In Go before 1.10.6 and 1.11.x before 1.11.3, the "go get" command is vulnerable to directory traversal when executed with the import path of a malicious Go package which contains curly braces (both '{' and '}' characters). Specifically, it is only vulnerable in GOPATH mode, but not in module mode (the distinction is documented at https://golang.org/cmd/go/#hdr-Module_aware_go_get). The attacker can cause an arbitrary filesystem write, which can lead to code execution.

## References
- https://groups.google.com/forum/?pli=1#%21topic/golang-announce/Kw31K8G7Fi0
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00041.html
- http://www.securityfocus.com/bid/106228
- https://lists.debian.org/debian-lts-announce/2021/03/msg00014.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00015.html
- https://security.gentoo.org/glsa/201812-09
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16874
