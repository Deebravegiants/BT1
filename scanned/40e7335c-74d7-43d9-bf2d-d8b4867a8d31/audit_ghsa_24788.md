# [C] Deserialization of Untrusted Data in JYaml

## Summary
Severity: Critical
Advisory: GHSA-4qhr-q7wf-94xp
CVE: CVE-2020-8441
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4qhr-q7wf-94xp
Type: github-advisory

## Affected
- Maven: `org.jyaml:jyaml` — affected >=0

## Details
JYaml through 1.3 allows remote code execution during deserialization of a malicious payload through the load() function. NOTE: this is a discontinued product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8441
- https://gist.github.com/j0lt-github/f5141abcacae63d434ecae211422153a
- https://github.com/mbechler/marshalsec
- https://github.com/mbechler/marshalsec/blob/master/marshalsec.pdf
- https://security.netapp.com/advisory/ntap-20200313-0001
- https://sourceforge.net/p/jyaml/bugs
