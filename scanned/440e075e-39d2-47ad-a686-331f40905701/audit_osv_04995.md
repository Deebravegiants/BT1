# [H] BIT-gitlab-2020-13359

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13359
Aliases: CVE-2020-13359
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13359
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.5.2

## Details
The Terraform API in GitLab CE/EE 12.10+ exposed the object storage signed URL on the delete operation allowing a malicious project maintainer to overwrite the Terraform state, bypassing audit and other business controls. Affected versions are >=12.10, <13.3.9,>=13.4, <13.4.5,>=13.5, <13.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13359.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/250266
- https://nvd.nist.gov/vuln/detail/CVE-2020-13359
