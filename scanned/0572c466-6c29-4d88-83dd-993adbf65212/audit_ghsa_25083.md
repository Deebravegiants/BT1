# [M] Improper Neutralization of Input During Web Page Generation in JavaMelody

## Summary
Severity: Medium
Advisory: GHSA-p4mx-p49m-8rw4
CVE: CVE-2013-4378
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p4mx-p49m-8rw4
Type: github-advisory

## Affected
- Maven: `net.bull.javamelody:javamelody-core` — affected >=0 <1.47.0

## Details
Cross-site scripting (XSS) vulnerability in HtmlSessionInformationsReport.java in JavaMelody 1.46 and earlier allows remote attackers to inject arbitrary web script or HTML via a crafted X-Forwarded-For header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4378
- https://github.com/javamelody/javamelody/issues/346
- https://github.com/javamelody/javamelody/commit/aacbc46151ff4ac1ca34ce0899c2a6113071c66e
- https://code.google.com/p/javamelody/issues/detail?id=346
- https://code.google.com/p/javamelody/source/detail?r=3515
- https://code.google.com/p/javamelody/wiki/ReleaseNotes
- http://osvdb.org/97778
- http://seclists.org/oss-sec/2013/q3/679
