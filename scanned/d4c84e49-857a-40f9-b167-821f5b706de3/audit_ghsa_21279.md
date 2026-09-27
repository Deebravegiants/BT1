# [C] gajira-create GitHub action vulnerable to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-4xqx-pqpj-9fqw
CVE: CVE-2020-14188
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-4xqx-pqpj-9fqw
Type: github-advisory

## Affected
- GitHub Actions: `atlassian/gajira-create` — affected >=0 <2.0.1

## Details
### Impact
An attacker can execute arbitrary code in the context of a GitHub runner by creating a specially crafted GitHub issue.

### Patches
This issue is patched in gajira-create version 2.0.1.

### Workarounds
There are no known workarounds.

### References
[GitHub Security Lab advisory GHSL-2020-172](https://securitylab.github.com/advisories/GHSL-2020-172-gajira-create-action)

## References
- https://github.com/atlassian/gajira-create/security/advisories/GHSA-4xqx-pqpj-9fqw
- https://nvd.nist.gov/vuln/detail/CVE-2020-14188
- https://github.com/atlassian/gajira-create
