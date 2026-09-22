# [M] CVE-2016-3116

## Summary
Severity: Medium
Advisory: CVE-2016-3116
CVSS: 6.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2016-03-22
Source: https://osv.dev/vulnerability/CVE-2016-3116
Type: osv

## Details
CRLF injection vulnerability in Dropbear SSH before 2016.72 allows remote authenticated users to bypass intended shell-command restrictions via crafted X11 forwarding data.

## References
- http://seclists.org/fulldisclosure/2016/Mar/47
- https://github.com/tintinweb/pub/tree/master/pocs/cve-2016-3115
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/179261.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/179269.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/179870.html
- https://matt.ucc.asn.au/dropbear/CHANGES
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00105.html
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00113.html
- http://packetstormsecurity.com/files/136251/Dropbear-SSHD-xauth-Command-Injection-Bypass.html
- https://security.gentoo.org/glsa/201607-08
