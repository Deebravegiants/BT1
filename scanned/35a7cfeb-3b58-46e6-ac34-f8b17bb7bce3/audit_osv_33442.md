# [M] FCGI versions 0.44 through 0.82, for Perl, include a vulnerable version of the FastCGI fcgi2 (aka fcgi) library

## Summary
Severity: Medium
Advisory: CVE-2025-40907
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-40907
Type: osv

## Details
FCGI versions 0.44 through 0.82, for Perl, include a vulnerable version of the FastCGI fcgi2 (aka fcgi) library.

The included FastCGI library is affected by  CVE-2025-23016, causing an integer overflow (and resultant heap-based buffer overflow) via crafted nameLen or valueLen values in data to the IPC socket. This occurs in ReadParams in fcgiapp.c.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40907.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40907
- https://github.com/FastCGI-Archives/fcgi2/issues/67
- https://github.com/perl-catalyst/FCGI/issues/14
- https://github.com/FastCGI-Archives/fcgi2/releases/tag/2.4.5
- https://patch-diff.githubusercontent.com/raw/FastCGI-Archives/fcgi2/pull/74.patch
- https://github.com/FastCGI-Archives/fcgi2
- http://www.openwall.com/lists/oss-security/2025/04/23/4
- https://www.synacktiv.com/en/publications/cve-2025-23016-exploiting-the-fastcgi-library
