# [M] BlazeMeter Jenkins Plugin is Missing Authorization for Available Resources

## Summary
Severity: Medium
Advisory: GHSA-fxp5-37mh-vff5
CVE: CVE-2025-13472
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-fxp5-37mh-vff5
Type: github-advisory

## Affected
- Maven: `com.blazemeter.plugins:BlazeMeterJenkinsPlugin` — affected >=0 <4.27

## Details
A fix was made in BlazeMeter Jenkins Plugin version 4.27 to allow users only with certain permissions to see the list of available resources like credential IDs, bzm workspaces and bzm project Ids. Prior to this fix, anyone could see this list as a dropdown on the Jenkins UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13472
- https://github.com/jenkinsci/blazemeter-plugin/commit/9fe5ed70f063c18fd6b64bb4db3cbdb612f653d4
- https://github.com/jenkinsci/blazemeter-plugin
- https://portal.perforce.com/s/cve/a91Qi000002bFgTIAU/missing-authorization-in-blazemeter-jenkins-plugin
