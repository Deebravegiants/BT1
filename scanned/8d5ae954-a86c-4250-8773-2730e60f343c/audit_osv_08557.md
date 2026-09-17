# [M] CVE-2016-4415

## Summary
Severity: Medium
Advisory: CVE-2016-4415
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-01
Source: https://osv.dev/vulnerability/CVE-2016-4415
Type: osv

## Details
wiretap/vwr.c in the Ixia IxVeriWave file parser in Wireshark 2.x before 2.0.2 incorrectly increases a certain octet count, which allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) via a crafted file.

## References
- https://www.wireshark.org/security/wnpa-sec-2016-12.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11795
- https://code.google.com/p/google-security-research/issues/detail?id=647
