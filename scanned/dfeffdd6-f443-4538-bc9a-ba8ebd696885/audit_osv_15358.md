# [M] CVE-2019-15635

## Summary
Severity: Medium
Advisory: CVE-2019-15635
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-23
Source: https://osv.dev/vulnerability/CVE-2019-15635
Type: osv

## Details
An issue was discovered in Grafana 5.4.0. Passwords for data sources used by Grafana (e.g., MySQL) are not encrypted. An admin user can reveal passwords for any data source by pressing the "Save and test" button within a data source's settings menu. When watching the transaction with Burp Proxy, the password for the data source is revealed and sent to the server. From a browser, a prompt to save the credentials is generated, and the password can be revealed by simply checking the "Show password" box.

## References
- https://exchange.xforce.ibmcloud.com/vulnerabilities/167244
- https://security.netapp.com/advisory/ntap-20191009-0002/
