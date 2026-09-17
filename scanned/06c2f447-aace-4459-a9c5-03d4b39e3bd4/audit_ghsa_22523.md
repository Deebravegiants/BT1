# [H] Vault GitHub Action did not correctly mask multi-line secrets in output

## Summary
Severity: High
Advisory: GHSA-4mgv-m5cm-f9h7
CVE: CVE-2021-32074
CWE: CWE-532
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4mgv-m5cm-f9h7
Type: github-advisory

## Affected
- GitHub Actions: `hashicorp/vault-action` — affected >=0 <2.2.0

## Details
HashiCorp vault-action (aka Vault GitHub Action) before 2.2.0 allows attackers to obtain sensitive information from log files because a multi-line secret was not correctly registered with GitHub Actions for log masking.

The vault-action implementation did not correctly handle the marking of multi-line variables. As a result, multi-line secrets were not correctly masked in vault-action output.

Remediation:
Customers using vault-action should evaluate the risk associated with this issue, and consider upgrading to vault-action 2.2.0 or newer. Please refer to https://github.com/marketplace/actions/hashicorp-vault for more information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32074
- https://github.com/hashicorp/vault-action/issues/205
- https://github.com/hashicorp/vault-action/pull/208
- https://github.com/hashicorp/vault-action/commit/3526e1be65cf8faf42d6088bc5da8bff596c718a
- https://discuss.hashicorp.com/t/hcsec-2021-13-vault-github-action-did-not-correctly-mask-multi-line-secrets-in-output/24128
- https://github.com/hashicorp/vault-action
- https://github.com/hashicorp/vault-action/blob/master/CHANGELOG.md
