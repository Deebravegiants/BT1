# [M] CVE-2021-21621

## Summary
Severity: Medium
Advisory: CVE-2021-21621
Aliases: GHSA-92pg-8g57-hqpx
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-02-24
Source: https://osv.dev/vulnerability/CVE-2021-21621
Type: osv

## Details
Jenkins Support Core Plugin 2.72 and earlier provides the serialized user authentication as part of the "About user (basic authentication details only)" information, which can include the session ID of the user creating the support bundle in some configurations.

## References
- https://www.jenkins.io/security/advisory/2021-02-24/#SECURITY-2150
