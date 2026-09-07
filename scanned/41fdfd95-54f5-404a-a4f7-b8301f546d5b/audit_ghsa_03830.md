# [C] MadsKristensen.AspNetCore.Miniblog subject to Improper Input Validation

## Summary
Severity: Critical
Advisory: GHSA-958r-g534-ccmr
CVE: CVE-2019-9845
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-958r-g534-ccmr
Type: github-advisory

## Affected
- NuGet: `MadsKristensen.AspNetCore.Miniblog` — affected >=0

## Details
madskristensen Miniblog.Core through 2019-01-16 allows remote attackers to execute arbitrary ASPX code via an IMG element with a data: URL, because SaveFilesToDisk in Controllers/BlogController.cs writes a decoded base64 string to a file without validating the extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9845
- https://github.com/advisories/GHSA-958r-g534-ccmr
- https://github.com/madskristensen/Miniblog.Core
- https://github.com/madskristensen/Miniblog.Core/blob/master/src/Controllers/BlogController.cs#L142
- https://rastating.github.io/miniblog-remote-code-execution
