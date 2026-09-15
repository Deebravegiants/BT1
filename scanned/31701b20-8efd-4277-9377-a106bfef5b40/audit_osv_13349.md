# [H] CVE-2018-19492

## Summary
Severity: High
Advisory: CVE-2018-19492
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-23
Source: https://osv.dev/vulnerability/CVE-2018-19492
Type: osv

## Details
An issue was discovered in cairo.trm in Gnuplot 5.2.5. This issue allows an attacker to conduct a buffer overflow with an arbitrary amount of data in the cairotrm_options function. This flaw is caused by a missing size check of an argument passed to the "set font" function. This issue occurs when the Gnuplot pngcairo terminal is used as a backend.

## References
- https://usn.ubuntu.com/4541-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00066.html
- https://lists.debian.org/debian-lts-announce/2018/11/msg00031.html
- https://lists.debian.org/debian-lts-announce/2018/11/msg00035.html
- https://sourceforge.net/p/gnuplot/gnuplot-main/ci/d5020716834582b20a5e12cdd49f39ee4f9dd949/
- https://sourceforge.net/p/gnuplot/bugs/2089/
