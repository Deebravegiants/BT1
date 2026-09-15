# [C] CVE-2022-48623

## Summary
Severity: Critical
Advisory: CVE-2022-48623
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/CVE-2022-48623
Type: osv

## Details
The Cpanel::JSON::XS package before 4.33 for Perl performs out-of-bounds accesses in a way that allows attackers to obtain sensitive information or cause a denial of service.

## References
- https://metacpan.org/release/RURBAN/Cpanel-JSON-XS-4.33/changes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48623.json
- https://github.com/briandfoy/cpan-security-advisory/blob/9374f98bef51e1ae887f293234050551c079776f/cpansa/CPANSA-Cpanel-JSON-XS.yml#L25-L36
- https://nvd.nist.gov/vuln/detail/CVE-2022-48623
- https://github.com/rurban/Cpanel-JSON-XS/issues/208
- https://github.com/rurban/Cpanel-JSON-XS/commit/41f32396eee9395a40f9ed80145c37622560de9b
