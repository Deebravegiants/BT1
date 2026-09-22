# [H] CVE-2023-3341

## Summary
Severity: High
Advisory: CVE-2023-3341
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-20
Source: https://osv.dev/vulnerability/CVE-2023-3341
Type: osv

## Details
The code that processes control channel messages sent to `named` calls certain functions recursively during packet parsing. Recursion depth is only limited by the maximum accepted packet size; depending on the environment, this may cause the packet-parsing code to run out of available stack memory, causing `named` to terminate unexpectedly. Since each incoming control channel message is fully parsed before its contents are authenticated, exploiting this flaw does not require the attacker to hold a valid RNDC key; only network access to the control channel's configured TCP port is necessary.
This issue affects BIND 9 versions 9.2.0 through 9.16.43, 9.18.0 through 9.18.18, 9.19.0 through 9.19.16, 9.9.3-S1 through 9.16.43-S1, and 9.18.0-S1 through 9.18.18-S1.

## References
- https://kb.isc.org/docs/cve-2023-3341
- https://lists.debian.org/debian-lts-announce/2024/01/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VSK5V4W4OHPM3JTJGWAQD6CZW7SFD75B/
- https://security.netapp.com/advisory/ntap-20231013-0003/
- https://www.debian.org/security/2023/dsa-5504
- http://www.openwall.com/lists/oss-security/2023/09/20/2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPJLLTJCSDJJII7IIZPLTBQNWP7MZH7F/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U35OARLQCPMVCBBPHWBXY5M6XJLD2TZ5/
