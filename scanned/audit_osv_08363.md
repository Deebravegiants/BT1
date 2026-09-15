# [M] CVE-2016-2531

## Summary
Severity: Medium
Advisory: CVE-2016-2531
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2531
Type: osv

## Details
Off-by-one error in epan/dissectors/packet-rsl.c in the RSL dissector in Wireshark 1.12.x before 1.12.10 and 2.0.x before 2.0.2 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted packet that triggers a 0xff tag value, a different vulnerability than CVE-2016-2530.

## References
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00015.html
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00016.html
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=de65fd6b00d0b891930324b9549c93ccfe9cac30
- http://www.debian.org/security/2016/dsa-3516
- http://www.wireshark.org/security/wnpa-sec-2016-10.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11829
- https://security.gentoo.org/glsa/201604-05
