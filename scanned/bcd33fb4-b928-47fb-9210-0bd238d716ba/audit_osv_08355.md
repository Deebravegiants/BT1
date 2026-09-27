# [M] CVE-2016-2523

## Summary
Severity: Medium
Advisory: CVE-2016-2523
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2523
Type: osv

## Details
The dnp3_al_process_object function in epan/dissectors/packet-dnp.c in the DNP3 dissector in Wireshark 1.12.x before 1.12.10 and 2.0.x before 2.0.2 allows remote attackers to cause a denial of service (infinite loop) via a crafted packet.

## References
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00015.html
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00016.html
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=260afe11feb796d1fde992d8f8c133ebd950b573
- http://www.debian.org/security/2016/dsa-3516
- http://www.wireshark.org/security/wnpa-sec-2016-03.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11938
- https://security.gentoo.org/glsa/201604-05
