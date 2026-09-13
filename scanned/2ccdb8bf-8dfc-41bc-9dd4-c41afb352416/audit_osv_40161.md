# [M] Xorg-x11-server: xorg-x11-server-xwayland: xorg-x11-server: out-of-bounds read/write in glx changedrawableattributes

## Summary
Severity: Medium
Advisory: CVE-2026-50262
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-50262
Type: osv

## Details
An out-of-bounds read flaw was found in the X.Org X server and Xwayland in __glXDisp_ChangeDrawableAttributes(). A wrong size validation check can read a client-controlled number of bytes, exceeding the request buffer, leading to information disclosure. A write path also exists but requires byte-swapped clients which is disabled by default.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.x.org/archives/xorg-announce/2026-June/003702.html
- https://redhat.atlassian.net/browse/PSIRTSUPT-16950
- https://access.redhat.com/errata/RHSA-2026:26562
- https://access.redhat.com/errata/RHSA-2026:26566
- https://access.redhat.com/errata/RHSA-2026:26590
- https://access.redhat.com/errata/RHSA-2026:26610
- https://access.redhat.com/errata/RHSA-2026:26709
- https://access.redhat.com/errata/RHSA-2026:28923
- https://access.redhat.com/errata/RHSA-2026:29844
- https://access.redhat.com/errata/RHSA-2026:36083
- https://access.redhat.com/errata/RHSA-2026:36085
- https://access.redhat.com/errata/RHSA-2026:36086
- https://access.redhat.com/errata/RHSA-2026:36087
- https://access.redhat.com/errata/RHSA-2026:36632
- https://access.redhat.com/errata/RHSA-2026:36633
- https://access.redhat.com/errata/RHSA-2026:36634
- https://access.redhat.com/errata/RHSA-2026:36768
- https://access.redhat.com/errata/RHSA-2026:36791
- https://access.redhat.com/errata/RHSA-2026:36792
