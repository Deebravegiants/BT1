# [M] OpenBao LDAP MFA Enforcement Bypass When Using Username As Alias

## Summary
Severity: Medium
Advisory: GHSA-2q8q-8fgw-9p6p
CVE: CVE-2025-55001
CWE: CWE-156
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-2q8q-8fgw-9p6p
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0 <2.3.2
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20250807212521-c52795c1ef74

## Details
### Impact

OpenBao allows assignment of policies and MFA attribution based upon entity aliases, chosen by the underlying auth method. When using the `username_as_alias=true` parameter in the LDAP auth method, the caller-supplied username is used verbatim without normalization, allowing an attacker to bypass alias-specific MFA requirements.

### Patches

OpenBao v2.3.2 will patch this issue.

### Workarounds

LDAP methods are only vulnerable if using `username_as_alias=true`. Remove all usage of this parameter and update any entity aliases accordingly.

### References

This issue was disclosed to HashiCorp and is the OpenBao equivalent of the following tickets:

- https://discuss.hashicorp.com/t/hcsec-2025-20-vault-ldap-mfa-enforcement-bypass-when-using-username-as-alias/76092
- https://nvd.nist.gov/vuln/detail/CVE-2025-6013

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-2q8q-8fgw-9p6p
- https://nvd.nist.gov/vuln/detail/CVE-2025-55001
- https://nvd.nist.gov/vuln/detail/CVE-2025-6013
- https://github.com/openbao/openbao/commit/c52795c1ef746c7f2c510f9225aa8ccbbd44f9fc
- https://discuss.hashicorp.com/t/hcsec-2025-20-vault-ldap-mfa-enforcement-bypass-when-using-username-as-alias/76092
- https://github.com/openbao/openbao
