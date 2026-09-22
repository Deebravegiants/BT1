# [C] Server side NTLM does not properly check parameters in FreeRDP

## Summary
Severity: Critical
Advisory: CVE-2022-24882
Aliases: GHSA-6x5p-gp49-3jhh
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-04-26
Source: https://osv.dev/vulnerability/CVE-2022-24882
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP). In versions prior to 2.7.0, NT LAN Manager (NTLM) authentication does not properly abort when someone provides and empty password value. This issue affects FreeRDP based RDP Server implementations. RDP clients are not affected. The vulnerability is patched in FreeRDP 2.7.0. There are currently no known workarounds.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/2.7.0
- https://lists.debian.org/debian-lts-announce/2025/02/msg00034.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24882.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-6x5p-gp49-3jhh
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AELSWWBAM2YONRPGLWVDY6UNTLJERJYL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DOYKBQOHSRM7JQYUIYUWFOXI2JZ2J5RD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PZWR6KSIKXO4B2TXBB3WH6YTNYHN46OY/
- https://nvd.nist.gov/vuln/detail/CVE-2022-24882
- https://security.gentoo.org/glsa/202210-24
- https://gitlab.gnome.org/GNOME/gnome-remote-desktop/-/issues/95
- https://github.com/FreeRDP/FreeRDP/pull/7750
