# [H] BIT-artifactory-2020-7931

## Summary
Severity: High
Advisory: BIT-artifactory-2020-7931
Aliases: CVE-2020-7931
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-artifactory-2020-7931
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=6.15.0 <6.15.1

## Details
In JFrog Artifactory 5.x and 6.x, insecure FreeMarker template processing leads to remote code execution, e.g., by modifying a .ssh/authorized_keys file. Patches are available for various versions between 5.11.8 and 6.16.0. The issue exists because use of the DefaultObjectWrapper class makes certain Java functions accessible to a template.

## References
- https://github.com/atredispartners/advisories/blob/master/ATREDIS-2019-0006.md
- https://www.jfrog.com/confluence/display/RTF/Release+Notes
- https://nvd.nist.gov/vuln/detail/CVE-2020-7931
