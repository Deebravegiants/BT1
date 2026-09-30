# [H] Date::Manip versions through 7.00 for Perl allow CPU exhaustion via quadratic backtracking in the unanchored time substitution in _parse_time

## Summary
Severity: High
Advisory: CVE-2026-60075
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-60075
Type: osv

## Details
Date::Manip versions through 7.00 for Perl allow CPU exhaustion via quadratic backtracking in the unanchored time substitution in _parse_time.

_parse_time removes a time from anywhere in the string with the unanchored substitution `s/$timerx/ /`, where $timerx is an auto-generated alternation of time patterns reached through a leading `(?:$atrx|^|\s+)`. The engine therefore retries the match at every position of an interior whitespace run: at each start position the leading `\s+` consumes the rest of the run greedily, the time alternation fails because the run holds no digits, and the engine backtracks a space at a time across the run before advancing the start position, which is quadratic in the length of the run. No time need be present in the string for this to happen, only a long run of whitespace, and the parse time rises about fourfold for each doubling of the run: a few kilobytes of whitespace costs seconds of CPU per parse and tens of kilobytes costs minutes.

Any caller that passes an untrusted string of unbounded length to ParseDate(), Date::Manip::Date->parse() or ->parse_time() can be made to spend unbounded CPU in a single parse, a denial of service.

## References
- http://www.openwall.com/lists/oss-security/2026/07/30/20
- https://cpan.org/modules
- https://metacpan.org/release/SBECK/Date-Manip-6.99/source/lib/Date/Manip/Date.pm#L1526
- https://metacpan.org/release/SBECK/Date-Manip-6.99/source/lib/Date/Manip/Date.pm#L1811
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60075.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-60075
- https://github.com/SBECK-github/Date-Manip/pull/55
- https://security.metacpan.org/patches/D/Date-Manip/6.99/CVE-2026-60075-r1.patch
- https://github.com/SBECK-github/Date-Manip
