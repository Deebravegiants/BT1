# [C] Code execution in Apache Struts 1 plugin

## Summary
Severity: Critical
Advisory: GHSA-29rm-6752-gvwv
CVE: CVE-2017-9791
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-29rm-6752-gvwv
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-struts1-plugin` — affected >=0

## Details
The Struts 1 plugin used with Apache Struts 2.1.x and 2.3.x might allow remote code execution via a malicious field value passed in a raw message to the ActionMessage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9791
- https://github.com/apache/struts/commit/ffe0e20edd9d5386f4410fddd970286a69373243
- https://security.netapp.com/advisory/ntap-20180706-0002
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2017-9791
- https://www.exploit-db.com/exploits/42324
- https://www.exploit-db.com/exploits/44643
- http://struts.apache.org/docs/s2-048.html
- http://www.oracle.com/technetwork/security-advisory/alert-cve-2017-9805-3889403.html
- http://www.securityfocus.com/bid/99484
- http://www.securitytracker.com/id/1038838
