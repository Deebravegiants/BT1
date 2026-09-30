# [H] DNN (aka DotNetNuke) has Remote Code Execution via a cookie

## Summary
Severity: High
Advisory: GHSA-x2rg-fmcv-crq5
CVE: CVE-2017-9822
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-x2rg-fmcv-crq5
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <9.1.1

## Details
DNN (aka DotNetNuke) before 9.1.1 has Remote Code Execution via a cookie, aka "2017-08 (Critical) Possible remote code execution on DNN sites."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9822
- https://github.com/advisories/GHSA-x2rg-fmcv-crq5
- http://packetstormsecurity.com/files/157080/DotNetNuke-Cookie-Deserialization-Remote-Code-Execution.html
- http://www.dnnsoftware.com/community/security/security-center
- http://www.securityfocus.com/bid/102213
