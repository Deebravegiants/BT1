# [H] CVE-2019-14523

## Summary
Severity: High
Advisory: CVE-2019-14523
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/CVE-2019-14523
Type: osv

## Details
An issue was discovered in Schism Tracker through 20190722. There is an integer underflow via a large plen in fmt_okt_load_song in the Amiga Oktalyzer parser in fmt/okt.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00083.html
- https://github.com/schismtracker/schismtracker/releases/tag/20190805
- https://security.gentoo.org/glsa/202107-12
- https://github.com/schismtracker/schismtracker/issues/202
