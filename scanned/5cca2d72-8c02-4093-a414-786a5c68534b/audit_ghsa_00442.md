# [C] The installation wizard in DotNetNuke (DNN) allows privilege escalation

## Summary
Severity: Critical
Advisory: GHSA-x8f7-h444-97w4
CVE: CVE-2015-2794
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-x8f7-h444-97w4
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <7.4.1

## Details
The installation wizard in DotNetNuke (DNN) before 7.4.1 allows remote attackers to reinstall the application and gain SuperUser access via a direct request to Install/InstallWizard.aspx.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2794
- https://dotnetnuke.codeplex.com/releases/view/615317
- https://github.com/advisories/GHSA-x8f7-h444-97w4
- https://www.exploit-db.com/exploits/39777
- http://www.dnnsoftware.com/community-blog/cid/155198/workaround-for-potential-security-issue
- http://www.dnnsoftware.com/community/security/security-center
- http://www.securityfocus.com/bid/96373
