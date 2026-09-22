# [M] IO::Uncompress::Unzip versions before 2.215 for Perl propagate uncaught exception when parsing zip header with malformed DOS date

## Summary
Severity: Medium
Advisory: CVE-2025-15649
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2025-15649
Type: osv

## Details
IO::Uncompress::Unzip versions before 2.215 for Perl propagate uncaught exception when parsing zip header with malformed DOS date.

_dosToUnixTime() decodes the local-file-header last-modification date field and calls Time::Local::timelocal() without an eval guard. A header whose date field decodes to an out-of-range month, day, or hour causes timelocal() to die.

The exception propagates out of IO::Uncompress::Unzip->new($file) where callers expect undef plus $UnzipError.

## References
- http://www.openwall.com/lists/oss-security/2026/05/27/1
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15649.json
- https://metacpan.org/release/PMQS/IO-Compress-2.215/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-15649
- https://github.com/pmqs/IO-Compress/issues/65
- https://github.com/pmqs/IO-Compress/commit/fd28c1d2374eee9811f6d0c5bddc0957abdf1da8.patch
- https://github.com/pmqs/IO-Compress
