# [M] CVE-2023-40345

## Summary
Severity: Medium
Advisory: CVE-2023-40345
Aliases: GHSA-wwww-xvm2-62w7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-08-16
Source: https://osv.dev/vulnerability/CVE-2023-40345
Type: osv

## Details
Jenkins Delphix Plugin 3.0.2 and earlier does not set the appropriate context for credentials lookup, allowing attackers with Overall/Read permission to access and capture credentials they are not entitled to.

## References
- https://support.delphix.com/Support_Policies_and_Technical_Bulletins/Technical_Bulletins/TB111_Delphix_Plugin_for_Jenkins_Vulnerable_to_Credential_Enumeration_and_Capture
- http://www.openwall.com/lists/oss-security/2023/08/16/3
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3214%20(2)
