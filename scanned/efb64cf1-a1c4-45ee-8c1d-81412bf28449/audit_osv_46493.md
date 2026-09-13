# [H] CVE-2012-1102

## Summary
Severity: High
Advisory: CVE-2012-1102
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-09
Source: https://osv.dev/vulnerability/CVE-2012-1102
Type: osv

## Details
It was discovered that the XML::Atom Perl module before version 0.39 did not disable external entities when parsing XML from potentially untrusted sources. This may allow attackers to gain read access to otherwise protected resources, depending on how the library is used.

## References
- https://metacpan.org/release/MIYAGAWA/XML-Atom-0.39/source/Changes
- https://seclists.org/oss-sec/2012/q1/549
- https://seclists.org/oss-sec/2012/q1/549
- https://seclists.org/oss-sec/2012/q1/549
