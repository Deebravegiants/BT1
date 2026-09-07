# [H] Code injection in port-killer

## Summary
Severity: High
Advisory: GHSA-2548-q746-x5x6
CVE: CVE-2021-23359
CWE: CWE-20, CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-2548-q746-x5x6
Type: github-advisory

## Affected
- npm: `port-killer` — affected >=0

## Details
This affects all versions of package port-killer. If (attacker-controlled) user input is given, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization. Running this PoC will cause the command touch success to be executed, leading to the creation of a file called success.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23359
- https://github.com/tylerjpeterson/port-killer/blob/1ca3a99ad80cc9ed5498d12b185189c10329025b/index.js%23L19
- https://snyk.io/vuln/SNYK-JS-PORTKILLER-1078533
