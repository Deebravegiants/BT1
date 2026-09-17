# [M] CVE-2019-13032

## Summary
Severity: Medium
Advisory: CVE-2019-13032
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-28
Source: https://osv.dev/vulnerability/CVE-2019-13032
Type: osv

## Details
An issue was discovered in FlightCrew v0.9.2 and earlier. A NULL pointer dereference occurs in GetRelativePathToNcx() or GetRelativePathsToXhtmlDocuments() when a NULL pointer is passed to xc::XMLUri::isValidURI(). This affects third-party software (not Sigil) that uses FlightCrew as a library.

## References
- https://salvatoresecurity.com/fun-with-fuzzers-or-how-i-discovered-three-vulnerabilities-part-1-of-3/
- https://usn.ubuntu.com/4055-1/
- https://github.com/Sigil-Ebook/flightcrew/issues/53
