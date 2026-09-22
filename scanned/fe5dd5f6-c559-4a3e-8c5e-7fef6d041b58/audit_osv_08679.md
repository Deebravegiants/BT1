# [C] CVE-2016-5180

## Summary
Severity: Critical
Advisory: CVE-2016-5180
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-5180
Type: osv

## Details
Heap-based buffer overflow in the ares_create_query function in c-ares 1.x before 1.12.0 allows remote attackers to cause a denial of service (out-of-bounds write) or possibly execute arbitrary code via a hostname with an escaped trailing dot.

## References
- http://www.securityfocus.com/bid/93243
- https://c-ares.haxx.se/CVE-2016-5180.patch
- https://c-ares.haxx.se/adv_20160929.html
- https://source.android.com/security/bulletin/2017-01-01.html
- http://rhn.redhat.com/errata/RHSA-2017-0002.html
- http://www.debian.org/security/2016/dsa-3682
- http://www.ubuntu.com/usn/USN-3143-1
- https://security.gentoo.org/glsa/201701-28
- https://googlechromereleases.blogspot.in/2016/09/stable-channel-updates-for-chrome-os.html
