# [H] CVE-2021-29949

## Summary
Severity: High
Advisory: CVE-2021-29949
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-29949
Type: osv

## Details
When loading the shared library that provides the OTR protocol implementation, Thunderbird will initially attempt to open it using a filename that isn't distributed by Thunderbird. If a computer has already been infected with a malicious library of the alternative filename, and the malicious library has been copied to a directory that is contained in the search path for executable libraries, then Thunderbird will load the incorrect library. This vulnerability affects Thunderbird < 78.9.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1682101
