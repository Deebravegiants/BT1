# [H] String::Util versions before 1.36 for Perl are susceptible to a regular expression denial of service

## Summary
Severity: High
Advisory: CVE-2026-14895
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-14895
Type: osv

## Details
String::Util versions before 1.36 for Perl are susceptible to a regular expression denial of service.

The trim and rtrim functions stripped trailing whitespace with s/\s*$//u. Because \s* matches greedily and the $ anchor fails whenever a non-whitespace character follows the whitespace, the regex engine retries the match at each offset of a long whitespace run, producing quadratic backtracking. The fix replaces \s*$ with \s+$.

Any caller that passes untrusted input to trim or rtrim can trigger CPU exhaustion with a string containing a long run of whitespace.

## References
- http://www.openwall.com/lists/oss-security/2026/07/07/18
- https://cpan.org/modules
- https://metacpan.org/release/BAKERSCOT/String-Util-1.36/diff/BAKERSCOT/String-Util-1.35#lib/String/Util.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14895.json
- https://github.com/scottchiefbaker/String-Util/releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-14895
- https://github.com/scottchiefbaker/String-Util/commit/f8150867aaeb8f57c59601aefb2193f2caed8745.patch
- https://github.com/scottchiefbaker/String-Util
