# [M] CVE-2018-1066

## Summary
Severity: Medium
Advisory: CVE-2018-1066
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/CVE-2018-1066
Type: osv

## Details
The Linux kernel before version 4.11 is vulnerable to a NULL pointer dereference in fs/cifs/cifsencrypt.c:setup_ntlmv2_rsp() that allows an attacker controlling a CIFS server to kernel panic a client that has this server mounted, because an empty TargetInfo field in an NTLMSSP setup negotiation response is mishandled during session recovery.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://usn.ubuntu.com/3880-1/
- https://www.debian.org/security/2018/dsa-4187
- https://www.debian.org/security/2018/dsa-4188
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://usn.ubuntu.com/3880-2/
- http://www.securityfocus.com/bid/103378
- https://bugzilla.redhat.com/show_bug.cgi?id=1539599
- https://github.com/torvalds/linux/commit/cabfb3680f78981d26c078a26e5c748531257ebb
- https://patchwork.kernel.org/patch/10187633/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cabfb3680f78981d26c078a26e5c748531257ebb
