# [M] CVE-2015-8720

## Summary
Severity: Medium
Advisory: CVE-2015-8720
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8720
Type: osv

## Details
The dissect_ber_GeneralizedTime function in epan/dissectors/packet-ber.c in the BER dissector in Wireshark 1.12.x before 1.12.9 and 2.0.x before 2.0.1 improperly checks an sscanf return value, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-39.html
- https://security.gentoo.org/glsa/201604-05
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79814
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=921bb07115fbffc081ec56a5022b4a9d58db6d39
