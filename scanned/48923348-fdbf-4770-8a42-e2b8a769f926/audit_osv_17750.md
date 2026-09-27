# [C] CVE-2020-1946

## Summary
Severity: Critical
Advisory: CVE-2020-1946
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/CVE-2020-1946
Type: osv

## Details
In Apache SpamAssassin before 3.4.5, malicious rule configuration (.cf) files can be configured to run system commands without any output or errors. With this, exploits can be injected in a number of scenarios. In addition to upgrading to SA version 3.4.5, users should only use update channels or 3rd party .cf files from trusted places.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7V2SBVTKVLFFT36ECJQ7TQ7KAQCQZDRZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JFBFRIG5TX23NF4ND6OAKKY7I6TLRCCP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NKAXYBKBMQOLIW6UKASJCAZRBOIYS4RL/
- https://lists.debian.org/debian-lts-announce/2021/04/msg00000.html
- https://s.apache.org/3r1wh
- https://security.gentoo.org/glsa/202105-26
- https://www.debian.org/security/2021/dsa-4879
