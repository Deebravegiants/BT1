# [H] Text::CSV_XS versions before 1.62 for Perl have a use-after-free when registered callbacks extend the Perl argument stack, which may enable type confusion or memory corruption

## Summary
Severity: High
Advisory: CVE-2026-7111
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-7111
Type: osv

## Details
Text::CSV_XS versions before 1.62 for Perl have a use-after-free when registered callbacks extend the Perl argument stack, which may enable type confusion or memory corruption.

The Parse, print, getline, and getline_all methods invoke registered callbacks (for example after_parse, before_print, or on_error) and cache the Perl argument stack pointer across the call. If a callback extends the argument stack enough to trigger a reallocation, the return value is written through the stale pointer into the freed buffer, and the caller reads the original $self argument as the return value instead.

Calling code that expects parsed data from getline_all receives the Text::CSV_XS object in its place, leading to logic errors or crashes. Text::CSV_XS objects used without any registered callbacks are not affected.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/17
- https://cpan.org/modules
- https://lists.debian.org/debian-lts-announce/2026/06/msg00037.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7111.json
- https://metacpan.org/release/HMBRAND/Text-CSV_XS-1.62/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-7111
- https://github.com/cpan-authors/Text-CSV_XS/commit/c17f31a5f2bf36674748eb4b6e25672f0571a224.patch
- https://github.com/cpan-authors/Text-CSV_XS
