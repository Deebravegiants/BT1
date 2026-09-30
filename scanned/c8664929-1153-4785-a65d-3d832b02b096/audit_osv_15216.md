# [H] CVE-2019-14524

## Summary
Severity: High
Advisory: CVE-2019-14524
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/CVE-2019-14524
Type: osv

## Details
An issue was discovered in Schism Tracker through 20190722. There is a heap-based buffer overflow via a large number of song patterns in fmt_mtm_load_song in fmt/mtm.c, a different vulnerability than CVE-2019-14465.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00083.html
- https://github.com/schismtracker/schismtracker/releases/tag/20190805
- https://github.com/schismtracker/schismtracker/issues/201
