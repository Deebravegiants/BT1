# [H] Xorg-x11-server: xorg-x11-server-xwayland: xorg-x11-server: stack buffer overflow in xkb key types due to unchecked shift levels

## Summary
Severity: High
Advisory: CVE-2026-50258
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-50258
Type: osv

## Details
A stack-based buffer overflow flaw was found in the X.Org X server and Xwayland. The X server has multiple stack buffers sized XkbMaxShiftLevel * XkbNumKbdGroups but CheckKeyTypes() does not verify or clamp non-canonical key types to XkbMaxShiftLevel. A client can change key types to excessive shift levels and trigger stack overflows. This is caused by an incomplete fix of CVE-2025-26597. This may be used to crash the server, or for privilege escalation if the X server runs as root.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.x.org/archives/xorg-announce/2026-June/003702.html
- https://redhat.atlassian.net/browse/PSIRTSUPT-16950
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-50258.json
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
