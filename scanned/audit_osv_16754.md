# [H] CVE-2019-9578

## Summary
Severity: High
Advisory: CVE-2019-9578
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-05
Source: https://osv.dev/vulnerability/CVE-2019-9578
Type: osv

## Details
In devs.c in Yubico libu2f-host before 1.1.8, the response to init is misparsed, leaking uninitialized stack memory back to the device.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GMA4H6AZFYIR3LA5VKKEJZNCCIVMUCFQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S4YCFMSNMXZ7XC4U6WXPQA7JCXC6VOAJ/
- https://developers.yubico.com/libu2f-host/Release_Notes.html
- https://security.gentoo.org/glsa/202004-15
- https://github.com/Yubico/libu2f-host/commit/e4bb58cc8b6202a421e65f8230217d8ae6e16eb5
- https://blog.inhq.net/posts/yubico-libu2f-host-vuln-part2/
