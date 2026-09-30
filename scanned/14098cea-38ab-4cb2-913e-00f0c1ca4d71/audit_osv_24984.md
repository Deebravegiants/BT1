# [M] CVE-2023-29132

## Summary
Severity: Medium
Advisory: CVE-2023-29132
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-04-14
Source: https://osv.dev/vulnerability/CVE-2023-29132
Type: osv

## Details
Irssi 1.3.x and 1.4.x before 1.4.4 has a use-after-free because of use of a stale special collector reference. This occurs when printing of a non-formatted line is concurrent with printing of a formatted line.

## References
- https://irssi.org/security/irssi_sa_2023_03.txt
- https://www.openwall.com/lists/oss-security/2023/03/30/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29132.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29132
