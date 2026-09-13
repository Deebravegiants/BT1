# [H] CVE-2020-27786

## Summary
Severity: High
Advisory: CVE-2020-27786
Aliases: A-175769013, PUB-A-175769013
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-27786
Type: osv

## Details
A flaw was found in the Linux kernel’s implementation of MIDI, where an attacker with a local account and the permissions to issue ioctl commands to midi devices could trigger a use-after-free issue. A write to this specific memory while freed and before use causes the flow of execution to change and possibly allow for memory corruption or privilege escalation. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.netapp.com/advisory/ntap-20210122-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=1900933
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c1f6e3c818dd734c30f6a7eeebf232ba2cf3181d
- http://www.openwall.com/lists/oss-security/2020/12/03/1
