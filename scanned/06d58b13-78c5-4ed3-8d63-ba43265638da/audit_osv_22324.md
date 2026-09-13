# [H] CVE-2022-25208

## Summary
Severity: High
Advisory: CVE-2022-25208
Aliases: GHSA-fq56-c7rj-j3j9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2022-25208
Type: osv

## Details
A missing permission check in Jenkins Chef Sinatra Plugin 1.20 and earlier allows attackers with Overall/Read permission to have Jenkins send an HTTP request to an attacker-controlled URL and have it parse an XML response.

## References
- http://www.openwall.com/lists/oss-security/2022/02/15/2
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-1377
