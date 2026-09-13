# [H] CVE-2022-47745

## Summary
Severity: High
Advisory: CVE-2022-47745
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-19
Source: https://osv.dev/vulnerability/CVE-2022-47745
Type: osv

## Details
ZenTao 16.4 to 18.0.beta1 is vulnerable to SQL injection. After logging in with any user, you can complete SQL injection by constructing a special request and sending it to function importNotice.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47745.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47745
- https://github.com/easysoft/zentaopms/issues/106
- https://github.com/l3s10n/ZenTaoPMS_SqlInjection
