# [H] CVE-2019-19909

## Summary
Severity: High
Advisory: CVE-2019-19909
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-19
Source: https://osv.dev/vulnerability/CVE-2019-19909
Type: osv

## Details
An issue was discovered in Public Knowledge Project (PKP) pkp-lib before 3.1.2-2, as used in Open Journal Systems (OJS) before 3.1.2-2. Code injection can occur in the OJS report generator if an authenticated Journal Manager user visits a crafted URL, because unserialize is used.

## References
- https://github.com/pkp/pkp-lib/issues/5302
- https://pkp.sfu.ca/ojs/ojs_download/
- https://github.com/pkp/pkp-lib/compare/3_1_2-1...3_1_2-2
