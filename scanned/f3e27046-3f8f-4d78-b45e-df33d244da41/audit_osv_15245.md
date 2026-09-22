# [C] CVE-2019-14809

## Summary
Severity: Critical
Advisory: CVE-2019-14809
Aliases: GO-2022-0211
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/CVE-2019-14809
Type: osv

## Details
net/url in Go before 1.11.13 and 1.12.x before 1.12.8 mishandles malformed hosts in URLs, leading to an authorization bypass in some applications. This is related to a Host field with a suffix appearing in neither Hostname() nor Port(), and is related to a non-numeric port number. For example, an attacker can compose a crafted javascript:// URL that results in a hostname of google.com.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00076.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00038.html
- https://groups.google.com/forum/#%21topic/golang-announce/0uuMm1BwpHE
- https://groups.google.com/forum/#%21topic/golang-announce/65QixT3tcmg
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4BBP27PZGSY6OP6D26E5FW4GZKBFHNU7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LYO6E3H34C346D2E443GLXK7OK6KIYIQ/
- https://access.redhat.com/errata/RHSA-2019:3433
- https://seclists.org/bugtraq/2019/Aug/31
- https://www.debian.org/security/2019/dsa-4503
- https://github.com/golang/go/issues/29098
