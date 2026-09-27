# [H] Code injection via property expansion in SoapUI

## Summary
Severity: High
Advisory: GHSA-c2fp-mpmm-cqxv
CVE: CVE-2014-1202
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-c2fp-mpmm-cqxv
Type: github-advisory

## Affected
- Maven: `com.smartbear.soapui:soapui` — affected >=0 <4.6.4

## Details
The WSDL/WADL import functionality in SoapUI before 4.6.4 allows remote attackers to execute arbitrary Java code via a crafted request parameter in a WSDL file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1202
- https://github.com/SmartBear/soapui/commit/6373165649ad74257493c69dbc0569caa7e6b4a6
- https://github.com/SmartBear/soapui
- https://github.com/SmartBear/soapui/blob/master/RELEASENOTES.txt
- http://baraktawily.blogspot.com/2014/01/soapui-code-execution-vulnerability-cve.html
- http://packetstormsecurity.com/files/124773/SoapUI-Remote-Code-Execution.html
- http://www.exploit-db.com/exploits/30908
