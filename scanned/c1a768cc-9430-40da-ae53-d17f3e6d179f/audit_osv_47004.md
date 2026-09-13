# [M] CVE-2015-8718

## Summary
Severity: Medium
Advisory: CVE-2015-8718
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8718
Type: osv

## Details
Double free vulnerability in epan/dissectors/packet-nlm.c in the NLM dissector in Wireshark 1.12.x before 1.12.9 and 2.0.x before 2.0.1, when the "Match MSG/RES packets for async NLM" option is enabled, allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-37.html
- https://security.gentoo.org/glsa/201604-05
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79814
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=81dfe6d450ada42d12f20ac26a6d8ae2302df37e
