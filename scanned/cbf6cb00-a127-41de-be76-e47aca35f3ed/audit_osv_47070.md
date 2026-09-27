# [H] CVE-2015-8868

## Summary
Severity: High
Advisory: CVE-2015-8868
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-05-06
Source: https://osv.dev/vulnerability/CVE-2015-8868
Type: osv

## Details
Heap-based buffer overflow in the ExponentialFunction::ExponentialFunction function in Poppler before 0.40.0 allows remote attackers to cause a denial of service (memory corruption and crash) or possibly execute arbitrary code via an invalid blend mode in the ExtGState dictionary in a crafted PDF document.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2580.html
- http://www.debian.org/security/2016/dsa-3563
- http://www.ubuntu.com/usn/USN-2958-1
- https://security.gentoo.org/glsa/201611-15
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183107.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183142.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00068.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00077.html
- http://www.openwall.com/lists/oss-security/2016/04/12/1
- http://www.securityfocus.com/bid/89324
- https://bugs.freedesktop.org/show_bug.cgi?id=93476
- https://cgit.freedesktop.org/poppler/poppler/commit/?id=b3425dd3261679958cd56c0f71995c15d2124433
- https://poppler.freedesktop.org/releases.html
