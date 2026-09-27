# [H] HarfBuzz::Shaper versions before 0.032 for Perl contains a bundled library with a null pointer dereference vulnerability

## Summary
Severity: High
Advisory: CVE-2026-0943
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-0943
Type: osv

## Details
HarfBuzz::Shaper versions before 0.032 for Perl contains a bundled library with a null pointer dereference vulnerability. 

Versions before 0.032 contain HarfBuzz 8.4.0 or earlier bundled as hb_src.tar.gz in the source tarball, which is affected by CVE-2026-22693.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-22693
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0943.json
- https://metacpan.org/release/JV/HarfBuzz-Shaper-0.032/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-0943
- https://bugzilla.redhat.com/show_bug.cgi?id=2429296
- https://github.com/sciurius/perl-HarfBuzz-Shaper
