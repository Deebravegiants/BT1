# [M] CVE-2016-2532

## Summary
Severity: Medium
Advisory: CVE-2016-2532
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2532
Type: osv

## Details
The dissect_llrp_parameters function in epan/dissectors/packet-llrp.c in the LLRP dissector in Wireshark 1.12.x before 1.12.10 and 2.0.x before 2.0.2 does not limit the recursion depth, which allows remote attackers to cause a denial of service (memory consumption or application crash) via a crafted packet.

## References
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00015.html
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00016.html
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=4a2cd6c79ecbf2cb21f985f01ce1c1e3030285ec
- http://www.debian.org/security/2016/dsa-3516
- http://www.wireshark.org/security/wnpa-sec-2016-11.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12048
- https://security.gentoo.org/glsa/201604-05
