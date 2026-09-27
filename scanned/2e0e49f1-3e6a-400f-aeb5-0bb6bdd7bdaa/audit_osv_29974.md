# [H] CVE-2024-48208

## Summary
Severity: High
Advisory: CVE-2024-48208
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-48208
Type: osv

## Details
pure-ftpd before 1.0.52 is vulnerable to Buffer Overflow. There is an out of bounds read in the domlsd() function of the ls.c file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48208.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48208
- https://github.com/jedisct1/pure-ftpd/pull/176
