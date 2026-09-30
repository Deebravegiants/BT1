# [M] YAML::Syck versions before 1.36 for Perl has missing Null-Terminators which causes Out-of-Bounds Read and potential Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2025-11683
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-11683
Type: osv

## Details
YAML::Syck versions before 1.36 for Perl has missing null-terminators which causes out-of-bounds read and potential information disclosure

Missing null terminators in token.c leads to but-of-bounds read which allows adjacent variable to be read

The issue is seen with complex YAML files with a hash of all keys and empty values.  There is no indication that the issue leads to accessing memory outside that allocated to the module.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11683.json
- https://metacpan.org/dist/YAML-Syck/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-11683
- https://github.com/cpan-authors/YAML-Syck/pull/65
- https://github.com/cpan-authors/YAML-Syck
