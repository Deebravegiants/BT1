# [C] CVE-2021-42646

## Summary
Severity: Critical
Advisory: CVE-2021-42646
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-05-11
Source: https://osv.dev/vulnerability/CVE-2021-42646
Type: osv

## Details
XML External Entity (XXE) vulnerability in the file based service provider creation feature of the Management Console in WSO2 API Manager 2.6.0, 3.0.0, 3.1.0, 3.2.0, and 4.0.0; and WSO2 IS as Key Manager 5.7.0, 5.9.0, and 5.10.0; and WSO2 Identity Server 5.7.0, 5.8.0, 5.9.0, 5.10.0, and 5.11.0. Allows attackers to gain read access to sensitive information or cause a denial of service via crafted GET requests.

## References
- http://packetstormsecurity.com/files/167465/WSO2-Management-Console-XML-Injection.html
- http://seclists.org/fulldisclosure/2022/Jun/7
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2021/WSO2-2021-1289/
- https://github.com/wso2/carbon-identity-framework/pull/3472
