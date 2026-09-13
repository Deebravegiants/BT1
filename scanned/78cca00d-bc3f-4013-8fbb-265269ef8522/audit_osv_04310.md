# [H] Dependency on Vulnerable Third-Party Component in GitLab

## Summary
Severity: High
Advisory: BIT-consul-2023-5332
Aliases: BIT-gitlab-2023-5332, CVE-2023-5332
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2023-5332
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.2.0 <1.2.4

## Details
Patch in third party library Consul requires 'enable-script-checks' to be set to False. This was required to enable a patch by the vendor. Without this setting the patch could be bypassed. This only affects GitLab-EE.

## References
- https://gitlab.com/gitlab-org/omnibus-gitlab/-/issues/8171
- https://www.hashicorp.com/blog/protecting-consul-from-rce-risk-in-specific-configurations
- https://nvd.nist.gov/vuln/detail/CVE-2023-5332
