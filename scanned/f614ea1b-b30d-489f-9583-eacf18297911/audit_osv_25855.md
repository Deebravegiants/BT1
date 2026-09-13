# [C] MFA bypass in Apereo CAS

## Summary
Severity: Critical
Advisory: CVE-2023-4612
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-09
Source: https://osv.dev/vulnerability/CVE-2023-4612
Type: osv

## Details
Improper Authentication vulnerability in Apereo CAS in jakarta.servlet.http.HttpServletRequest.getRemoteAddr method allows Multi-Factor Authentication bypass.This issue affects CAS: through 7.0.0-RC7. It is unknown whether in new versions the issue will be fixed. For the date of publication there is no patch, and the vendor does not treat it as a vulnerability.

## References
- https://www.apereo.org/projects/cas
- https://cert.pl/en/posts/2023/11/CVE-2023-4612/
- https://cert.pl/posts/2023/11/CVE-2023-4612/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4612.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4612
