# [M] CuteSoft CuteEditor Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w327-wq28-3vmf
CVE: CVE-2009-4665
CWE: CWE-22
Ecosystem: NuGet
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-w327-wq28-3vmf
Type: github-advisory

## Affected
- NuGet: `CuteEditor` — affected >=0 <6.6

## Details
Directory traversal vulnerability in `CuteSoft_Client/CuteEditor/Load.ashx` in CuteSoft Components Cute Editor for ASP.NET allows remote attackers to read arbitrary files via a `..` (dot dot) in the file parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-4665
- https://exchange.xforce.ibmcloud.com/vulnerabilities/50727
- https://web.archive.org/web/20200228205122/http://www.securityfocus.com/bid/35085
- http://www.exploit-db.com/exploits/8785
