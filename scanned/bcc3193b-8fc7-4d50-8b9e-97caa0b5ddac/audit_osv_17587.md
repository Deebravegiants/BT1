# [H] CVE-2020-17367

## Summary
Severity: High
Advisory: CVE-2020-17367
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-11
Source: https://osv.dev/vulnerability/CVE-2020-17367
Type: osv

## Details
Firejail through 0.9.62 does not honor the -- end-of-options indicator after the --output option, which may lead to command injection.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JFXN3JJG4DIMN4TAHOTKFMS7SGM4EOTR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W66IR5YT4KG464SKEMQN2NP2LGATGEGS/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00036.html
- https://github.com/netblue30/firejail
- https://lists.debian.org/debian-lts-announce/2020/08/msg00033.html
- https://security.gentoo.org/glsa/202101-02
- https://www.debian.org/security/2020/dsa-4742
- https://www.debian.org/security/2020/dsa-4743
