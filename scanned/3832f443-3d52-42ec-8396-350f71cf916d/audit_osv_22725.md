# [M] CVE-2022-37033

## Summary
Severity: Medium
Advisory: CVE-2022-37033
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-01
Source: https://osv.dev/vulnerability/CVE-2022-37033
Type: osv

## Details
In dotCMS 5.x-22.06, TempFileAPI allows a user to create a temporary file based on a passed in URL, while attempting to block any SSRF access to local IP addresses or private subnets. In resolving this URL, the TempFileAPI follows any 302 redirects that the remote URL returns. Because there is no re-validation of the redirect URL, the TempFileAPI can be used to return data from those local/private hosts that should not be accessible remotely.

## References
- https://www.dotcms.com/security/SI-64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37033.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37033
