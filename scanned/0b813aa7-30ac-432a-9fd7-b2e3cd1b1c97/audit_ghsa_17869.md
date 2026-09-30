# [M] OpenBao Userpass and LDAP User Lockout Bypass

## Summary
Severity: Medium
Advisory: GHSA-j3xv-7fxp-gfhx
CVE: CVE-2025-54998
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-j3xv-7fxp-gfhx
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0 <2.3.2
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20250807212521-c52795c1ef74

## Details
### Impact

Attackers could bypass the automatic user lockout mechanisms in the OpenBao Userpass or LDAP auth systems. This was caused by different aliasing between pre-flight and full login request user entity alias attributions. 

### Patches

OpenBao v2.3.2 will patch this issue.

### Workarounds

Existing users may apply rate-limiting quotas on the authentication endpoints: https://openbao.org/api-docs/system/rate-limit-quotas/

### References

This issue was disclosed to HashiCorp and is the OpenBao equivalent of the following tickets:

- https://discuss.hashicorp.com/t/hcsec-2025-16-vault-userpass-and-ldap-user-lockout-bypass/76035
- https://nvd.nist.gov/vuln/detail/CVE-2025-6004

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-j3xv-7fxp-gfhx
- https://nvd.nist.gov/vuln/detail/CVE-2025-54998
- https://nvd.nist.gov/vuln/detail/CVE-2025-6004
- https://github.com/openbao/openbao/commit/c52795c1ef746c7f2c510f9225aa8ccbbd44f9fc
- https://discuss.hashicorp.com/t/hcsec-2025-16-vault-userpass-and-ldap-user-lockout-bypass/76035
- https://github.com/openbao/openbao
