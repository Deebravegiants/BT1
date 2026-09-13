# [M] CVE-2023-46655

## Summary
Severity: Medium
Advisory: CVE-2023-46655
Aliases: GHSA-9ggw-h9mf-4jh7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-46655
Type: osv

## Details
Jenkins CloudBees CD Plugin 1.1.32 and earlier follows symbolic links to locations outside of the directory from which artifacts are published during the 'CloudBees CD - Publish Artifact' post-build step, allowing attackers able to configure jobs to publish arbitrary files from the Jenkins controller file system to the previously configured CloudBees CD server.

## References
- https://www.jenkins.io/security/advisory/2023-10-25/#SECURITY-3238
- http://www.openwall.com/lists/oss-security/2023/10/25/2
