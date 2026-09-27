# [M] CVE-2024-53901

## Summary
Severity: Medium
Advisory: CVE-2024-53901
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-11-24
Source: https://osv.dev/vulnerability/CVE-2024-53901
Type: osv

## Details
The Imager package before 1.025 for Perl has a heap-based buffer overflow leading to denial of service, or possibly unspecified other impact, when the trim() method is called on a crafted input image.

## References
- https://metacpan.org/release/TONYC/Imager-1.025/changes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53901.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53901
- https://github.com/briandfoy/cpan-security-advisory/issues/167
- https://github.com/briandfoy/cpan-security-advisory/issues/171
- https://github.com/tonycoz/imager/issues/534
