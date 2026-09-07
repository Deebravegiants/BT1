# [C] Struts ParameterInterceptor vulnerability allows remote command execution

## Summary
Severity: Critical
Advisory: GHSA-j68f-8h6p-9h5q
CVE: CVE-2011-3923
CWE: CWE-732, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-j68f-8h6p-9h5q
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.3.1.2

## Details
Regular expression in ParametersInterceptor matches `top['foo'](0)` as a valid expression, which OGNL treats as `(top['foo'])(0)` and evaluates the value of 'foo' action parameter as an OGNL expression. This lets malicious users put arbitrary OGNL statements into any String variable exposed by an action and have it evaluated as an OGNL expression and since OGNL statement is in HTTP parameter value attacker can use blacklisted characters (e.g. #) to disable method execution and execute arbitrary methods, bypassing the ParametersInterceptor and OGNL library protections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3923
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-3923
- https://exchange.xforce.ibmcloud.com/vulnerabilities/72585
- https://security-tracker.debian.org/tracker/CVE-2011-3923
- https://web.archive.org/web/20140725074137/http://seclists.org/fulldisclosure/2014/Jul/38
- http://blog.o0o.nu/2012/01/cve-2011-3923-yet-another-struts2.html
- http://struts.apache.org/development/2.x/docs/s2-009.html
