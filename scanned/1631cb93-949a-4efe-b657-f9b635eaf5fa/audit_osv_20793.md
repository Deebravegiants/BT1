# [M] CVE-2021-3700

## Summary
Severity: Medium
Advisory: CVE-2021-3700
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/CVE-2021-3700
Type: osv

## Details
A use-after-free vulnerability was found in usbredir in versions prior to 0.11.0 in the usbredirparser_serialize() in usbredirparser/usbredirparser.c. This issue occurs when serializing large amounts of buffered write data in the case of a slow or blocked destination.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1992830
- https://gitlab.freedesktop.org/spice/usbredir/-/commit/03c519ff5831ba
