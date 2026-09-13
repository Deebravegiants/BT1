# [H] Insufficient Entropy in DotNetNuke

## Summary
Severity: High
Advisory: GHSA-pf46-gqg9-j3v3
CVE: CVE-2018-15812
CWE: CWE-331
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-pf46-gqg9-j3v3
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=9.2.0 <9.2.2

## Details
DNN (aka DotNetNuke) 9.2 through 9.2.1 incorrectly converts encryption key source values, resulting in lower than expected entropy.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15812
- https://github.com/dnnsoftware/Dnn.Platform/releases
- https://www.dnnsoftware.com/community/security/security-center
- http://packetstormsecurity.com/files/157080/DotNetNuke-Cookie-Deserialization-Remote-Code-Execution.html
