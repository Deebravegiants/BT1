# [H] OpenBao Root Namespace Operator May Elevate Token Privileges

## Summary
Severity: High
Advisory: GHSA-vf84-mxrq-crqc
CVE: CVE-2025-54996
CWE: CWE-266, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-vf84-mxrq-crqc
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0 <2.3.2
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20250806193240-9b0b5d4f345f

## Details
### Impact

Accounts with access to the highly-privileged identity entity system in the root namespace may increase their scope directly to the `root` policy. While the identity system always allowed adding arbitrary policies, which in turn could contain capability grants on arbitrary paths, the `root` policy is restricted to manual generation using unseal or recovery key shares. The global `root` policy is not accessible from child namespaces.

### Patches

OpenBao v2.3.2 will patch this issue.

### Workarounds

Use of `denied_parameters` in any policy which has access to the affected identity endpoints (on [identity entities](https://openbao.org/api-docs/secret/identity/entity/)) may be sufficient to prohibit this type of attack. 

### References

This issue was disclosed to HashiCorp and is the OpenBao equivalent of the following tickets:

- https://discuss.hashicorp.com/t/hcsec-2025-13-vault-root-namespace-operator-may-elevate-token-privileges/76032
- https://nvd.nist.gov/vuln/detail/cve-2025-5999

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-vf84-mxrq-crqc
- https://nvd.nist.gov/vuln/detail/CVE-2025-54996
- https://github.com/openbao/openbao/pull/1627
- https://github.com/openbao/openbao/commit/9b0b5d4f345fdfb1065956f042b12cbd86cd6e0f
- https://discuss.hashicorp.com/t/hcsec-2025-13-vault-root-namespace-operator-may-elevate-token-privileges/76032
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.3.2
- https://nvd.nist.gov/vuln/detail/cve-2025-5999
