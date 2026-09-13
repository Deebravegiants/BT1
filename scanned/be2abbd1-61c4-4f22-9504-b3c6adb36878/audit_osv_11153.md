# [M] CVE-2017-6414

## Summary
Severity: Medium
Advisory: CVE-2017-6414
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6414
Type: osv

## Details
Memory leak in the vcard_apdu_new function in card_7816.c in libcacard before 2.5.3 allows local guest OS users to cause a denial of service (host memory consumption) via vectors related to allocating a new APDU object.

## References
- http://www.securityfocus.com/bid/96541
- https://access.redhat.com/errata/RHSA-2017:2408
- https://cgit.freedesktop.org/spice/libcacard/tree/NEWS?id=aaa5251791bf0b1640afcba77a7d79ea23c42d53
- http://www.openwall.com/lists/oss-security/2017/03/01/11
- https://bugzilla.redhat.com/show_bug.cgi?id=1427833
- https://cgit.freedesktop.org/spice/libcacard/commit/?id=9113dc6a303604a2d9812ac70c17d076ef11886c
