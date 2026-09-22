# [H] HTTP::Date versions before 6.08 for Perl allow CPU exhaustion via polynomial regex backtracking in parse_date

## Summary
Severity: High
Advisory: CVE-2026-14741
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-14741
Type: osv

## Details
HTTP::Date versions before 6.08 for Perl allow CPU exhaustion via polynomial regex backtracking in parse_date.

parse_date() matches the date string against a chain of alternative regexes, and str2time() delegates to it. Several of these patterns place unbounded quantifiers next to each other before a trailing `\s*$` anchor. A valid date prefix followed by a long interior run of digits, letters, or whitespace and a single trailing byte that defeats the final match forces the engine to repartition the run, giving polynomial (about quadratic) backtracking. A header value of a few tens of kilobytes runs for tens of seconds of CPU.

HTTP::Date parses timestamps such as HTTP `Date`, `Expires`, and `Last-Modified` headers, which commonly originate from untrusted sources. Any caller that passes an untrusted date header to str2time() or parse_date() can be driven to consume unbounded CPU, a denial of service.

## References
- http://www.openwall.com/lists/oss-security/2026/07/17/10
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14741.json
- https://metacpan.org/release/OALDERS/HTTP-Date-6.08/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-14741
- https://github.com/libwww-perl/HTTP-Date/pull/33
- https://github.com/libwww-perl/HTTP-Date/commit/78c20952cdfbf11e03cf1199ad70f13298a84c5c.patch
- https://github.com/libwww-perl/HTTP-Date
