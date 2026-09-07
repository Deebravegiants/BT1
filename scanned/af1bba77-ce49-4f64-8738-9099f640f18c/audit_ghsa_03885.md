# [M] Stored Cross-Site Scripting vulnerability in admin component of DotNetNuke

## Summary
Severity: Medium
Advisory: GHSA-5whq-j5qg-wjvp
CVE: CVE-2019-12562
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-11-18
Source: https://github.com/advisories/GHSA-5whq-j5qg-wjvp
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <9.4.0

## Details
Cross-site scripting (XSS) is possible in DNN (formerly DotNetNuke) before 9.4.0 by remote authenticated users via the Display Name field in the admin notification function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12562
- https://mayaseven.com/cve-2019-12562-stored-cross-site-scripting-in-dotnetnuke-dnn-version-v9-3-2
- http://packetstormsecurity.com/files/154673/DotNetNuke-Cross-Site-Scripting.html
