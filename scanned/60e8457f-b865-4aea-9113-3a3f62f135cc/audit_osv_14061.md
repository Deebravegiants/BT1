# [C] CVE-2018-6836

## Summary
Severity: Critical
Advisory: CVE-2018-6836
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-08
Source: https://osv.dev/vulnerability/CVE-2018-6836
Type: osv

## Details
The netmonrec_comment_destroy function in wiretap/netmon.c in Wireshark through 2.4.4 performs a free operation on an uninitialized memory address, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=28960d79cca262ac6b974f339697b299a1e28fef
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14397
- https://code.wireshark.org/review/#/c/25660/
- https://code.wireshark.org/review/#/c/25660/2/wiretap/netmon.c
