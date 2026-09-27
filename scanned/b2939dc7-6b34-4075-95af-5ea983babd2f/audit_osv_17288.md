# [H] CVE-2020-14342

## Summary
Severity: High
Advisory: CVE-2020-14342
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/CVE-2020-14342
Type: osv

## Details
It was found that cifs-utils' mount.cifs was invoking a shell when requesting the Samba password, which could be used to inject arbitrary commands. An attacker able to invoke mount.cifs with special permission, such as via sudo rules, could use this flaw to escalate their privileges.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DUMRICFXJVCBBOSKZSKT3HFVQM6VPJU3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JBNFSTJOQWVPFZAUJNNMAPY45PW5RTTE/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00109.html
- https://security.gentoo.org/glsa/202009-16
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14342
- https://lists.samba.org/archive/samba-technical/2020-September/135747.html
