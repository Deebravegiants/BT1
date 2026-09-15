# [H] Perl is vulnerable to a heap buffer overflow when transliterating non-ASCII bytes

## Summary
Severity: High
Advisory: CVE-2024-56406
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-13
Source: https://osv.dev/vulnerability/CVE-2024-56406
Type: osv

## Details
A heap buffer overflow vulnerability was discovered in Perl. 

Release branches 5.34, 5.36, 5.38 and 5.40 are affected, including development versions from 5.33.1 through 5.41.10.

When there are non-ASCII bytes in the left-hand-side of the `tr` operator, `S_do_trans_invmap` can overflow the destination pointer `d`.

   $ perl -e '$_ = "\x{FF}" x 1000000; tr/\xFF/\x{100}/;' 
   Segmentation fault (core dumped)

It is believed that this vulnerability can enable Denial of Service and possibly Code Execution attacks on platforms that lack sufficient defenses.

## References
- http://www.openwall.com/lists/oss-security/2025/04/13/3
- http://www.openwall.com/lists/oss-security/2025/04/13/4
- http://www.openwall.com/lists/oss-security/2025/04/13/5
- https://cpan.org/modules
- https://github.com/Perl/perl5/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56406.json
- https://metacpan.org/release/SHAY/perl-5.38.4/changes
- https://metacpan.org/release/SHAY/perl-5.40.2/changes
- https://nvd.nist.gov/vuln/detail/CVE-2024-56406
- https://github.com/Perl/perl5/commit/87f42aa0e0096e9a346c9672aa3a0bd3bef8c1dd.patch
