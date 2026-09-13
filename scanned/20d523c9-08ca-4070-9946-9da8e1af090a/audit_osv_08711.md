# [H] CVE-2016-5384

## Summary
Severity: High
Advisory: CVE-2016-5384
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-13
Source: https://osv.dev/vulnerability/CVE-2016-5384
Type: osv

## Details
fontconfig before 2.12.1 does not validate offsets, which allows local users to trigger arbitrary free calls and consequently conduct double free attacks and execute arbitrary code via a crafted cache file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CJ45VRAMCIISHOVKFVOQYQUSTUJP7FC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GGOS4YYB7UYAWX5AEXJZHDIX4ZMSXSW5/
- http://rhn.redhat.com/errata/RHSA-2016-2601.html
- http://www.debian.org/security/2016/dsa-3644
- http://www.securityfocus.com/bid/92339
- http://www.ubuntu.com/usn/USN-3063-1
- https://cgit.freedesktop.org/fontconfig/commit/?id=7a4a5bd7897d216f0794ca9dbce0a4a5c9d14940
- https://lists.freedesktop.org/archives/fontconfig/2016-August/005792.html
