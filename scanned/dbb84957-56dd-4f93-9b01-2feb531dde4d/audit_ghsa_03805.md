# [H] Inadequate Encryption Strength in DotNetNuke

## Summary
Severity: High
Advisory: GHSA-j3g9-6fx5-gjv7
CVE: CVE-2018-18325
CWE: CWE-326
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N/E:H (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-j3g9-6fx5-gjv7
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <9.3.0

## Details
DNN (aka DotNetNuke) 9.2 through 9.2.2 uses a weak encryption algorithm to protect input parameters. NOTE: this issue exists because of an incomplete fix for CVE-2018-15811.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18325
- https://github.com/dnnsoftware/Dnn.Platform
- https://github.com/dnnsoftware/Dnn.Platform/releases
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2018-18325
- https://www.dnnsoftware.com/community/security/security-center
- http://packetstormsecurity.com/files/157080/DotNetNuke-Cookie-Deserialization-Remote-Code-Execution.html
