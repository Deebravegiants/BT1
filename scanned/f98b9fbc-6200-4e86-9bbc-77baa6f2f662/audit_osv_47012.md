# [M] CVE-2015-8726

## Summary
Severity: Medium
Advisory: CVE-2015-8726
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8726
Type: osv

## Details
wiretap/vwr.c in the VeriWave file parser in Wireshark 1.12.x before 1.12.9 and 2.0.x before 2.0.1 does not validate certain signature and Modulation and Coding Scheme (MCS) data, which allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted file.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-44.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11789
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11791
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79382
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=185911de7d337246044c8e99da2f5b4bac74c0d5
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=b8fa3d463c1bdd9b84c897441e7a5c8ad1f0f292
