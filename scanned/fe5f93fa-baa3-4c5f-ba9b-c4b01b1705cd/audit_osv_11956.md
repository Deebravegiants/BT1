# [M] CVE-2018-1000195

## Summary
Severity: Medium
Advisory: CVE-2018-1000195
Aliases: GHSA-rgmj-mccj-h9mx
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2018-1000195
Type: osv

## Details
A server-side request forgery vulnerability exists in Jenkins 2.120 and older, LTS 2.107.2 and older in ZipExtractionInstaller.java that allows users with Overall/Read permission to have Jenkins submit a HTTP GET request to an arbitrary URL and learn whether the response is successful (200) or not.

## References
- https://jenkins.io/security/advisory/2018-05-09/#SECURITY-794
- https://www.oracle.com/security-alerts/cpuapr2022.html
