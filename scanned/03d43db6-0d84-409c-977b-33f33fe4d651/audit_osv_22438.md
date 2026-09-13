# [C] CVE-2022-29464

## Summary
Severity: Critical
Advisory: CVE-2022-29464
CVSS: 9.8 (CVSS:3.1/AC:L/AV:N/A:H/C:H/I:H/PR:N/S:U/UI:N)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2022-29464
Type: osv

## Details
Certain WSO2 products allow unrestricted file upload with resultant remote code execution. The attacker must use a /fileupload endpoint with a Content-Disposition directory traversal sequence to reach a directory under the web root, such as a ../../../../repository/deployment/server/webapps directory. This affects WSO2 API Manager 2.2.0 up to 4.0.0, WSO2 Identity Server 5.2.0 up to 5.11.0, WSO2 Identity Server Analytics 5.4.0, 5.4.1, 5.5.0 and 5.6.0, WSO2 Identity Server as Key Manager 5.3.0 up to 5.11.0, WSO2 Enterprise Integrator 6.2.0 up to 6.6.0, WSO2 Open Banking AM 1.4.0 up to 2.0.0 and WSO2 Open Banking KM 1.4.0, up to 2.0.0.

## References
- http://packetstormsecurity.com/files/166921/WSO-Arbitrary-File-Upload-Remote-Code-Execution.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-29464
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29464.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-29464
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2022/WSO2-2021-1738/
- https://github.com/hakivvi/CVE-2022-29464
- http://www.openwall.com/lists/oss-security/2022/04/22/7
