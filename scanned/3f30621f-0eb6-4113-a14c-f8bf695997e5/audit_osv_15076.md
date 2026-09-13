# [H] CVE-2019-13241

## Summary
Severity: High
Advisory: CVE-2019-13241
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-04
Source: https://osv.dev/vulnerability/CVE-2019-13241
Type: osv

## Details
FlightCrew v0.9.2 and older are vulnerable to a directory traversal, allowing attackers to write arbitrary files via a ../ (dot dot slash) in a ZIP archive entry that is mishandled during extraction.

## References
- https://usn.ubuntu.com/4055-1/
- https://github.com/Sigil-Ebook/flightcrew/issues/52
- https://salvatoresecurity.com/fun-with-fuzzers-how-i-discovered-three-vulnerabilities-part-3-of-3/
