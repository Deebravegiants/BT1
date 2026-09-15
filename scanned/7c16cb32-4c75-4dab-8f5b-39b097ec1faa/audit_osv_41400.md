# [H] Date::Manip versions through 7.00 for Perl return corrupted dates via non-ASCII decimal digits that pass the numeric range tests in check

## Summary
Severity: High
Advisory: CVE-2026-60074
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-60074
Type: osv

## Details
Date::Manip versions through 7.00 for Perl return corrupted dates via non-ASCII decimal digits that pass the numeric range tests in check.

The parse regexes capture year, month and day with the `\d` shorthand, which on a character string matches the whole Unicode decimal digit property `\p{Nd}` and not just `[0-9]`. Date::Manip::Base::check then validates the captured fields with numeric comparisons alone (`$y<1 || $y>9999`, `$m<1 || $m>12`, `$d<1 || $d>$days`), and _parse_check stores the numified fields (`$y+0`). Perl truncates a string at the first character that is not an ASCII digit, so a field whose leading characters are ASCII digits numifies to an in-range prefix and satisfies every test: a year field of three ASCII digits followed by U+0664 ARABIC-INDIC DIGIT FOUR numifies to 202, giving the year 0202, and one non-ASCII digit in the month or day field shifts those fields the same way. The hour, minute and second fields match explicit ASCII character classes (`0?[0-9]`, `[0-5][0-9]`) and do not shift, though a non-ASCII digit in a fractional hour or minute field truncates the fraction.

Any caller that passes an untrusted character string to ParseDate() or Date::Manip::Date->parse() can get back a date that differs from the string it parsed, with no parse error. Where the parsed date gates logic such as an expiry check or a retention window, the shift goes unnoticed.

## References
- http://www.openwall.com/lists/oss-security/2026/07/30/19
- https://cpan.org/modules
- https://metacpan.org/release/SBECK/Date-Manip-6.99/source/lib/Date/Manip/Base.pm#L602-614
- https://metacpan.org/release/SBECK/Date-Manip-6.99/source/lib/Date/Manip/Date.pm#L1536-1539
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60074.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-60074
- https://github.com/SBECK-github/Date-Manip/pull/54
- https://security.metacpan.org/patches/D/Date-Manip/6.99/CVE-2026-60074-r1.patch
- https://github.com/SBECK-github/Date-Manip
