# [M] Server side object manipulation in Apache Struts

## Summary
Severity: Medium
Advisory: GHSA-x5fc-pgpx-59j5
CVE: CVE-2010-1870
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x5fc-pgpx-59j5
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.2.1

## Details
OGNL provides, among other features, extensive expression evaluation capabilities. This vulnerability allows a malicious user to bypass the '#'-usage protection built into the ParametersInterceptor, thus being able to manipulate server side context objects. This behavior was already addressed in [S2-003](https://cwiki.apache.org/confluence/display/WW/S2-003), but it turned out that the resulting fix based on whitelisting acceptable parameter names closed the vulnerability only partially.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1870
- https://cwiki.apache.org/confluence/display/WW/S2-003
- https://github.com/apache/struts
- http://blog.o0o.nu/2010/07/cve-2010-1870-struts2xwork-remote.html
- http://confluence.atlassian.com/display/FISHEYE/FishEye+Security+Advisory+2010-06-16
- http://packetstormsecurity.com/files/159643/LISTSERV-Maestro-9.0-8-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2010/Jul/183
- http://seclists.org/fulldisclosure/2020/Oct/23
- http://struts.apache.org/2.2.1/docs/s2-005.html
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20140709-struts2
