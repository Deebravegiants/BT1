# [C] Privileged OpenBao Operator May Execute Code on the Underlying Host

## Summary
Severity: Critical
Advisory: GHSA-xp75-r577-cvhp
CVE: CVE-2025-54997
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-xp75-r577-cvhp
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0 <2.3.2
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20250806194004-a14053c9679d

## Details
### Impact

Under certain threat models, OpenBao operators with privileged API access may not be system administrators and thus normally lack the ability to update binaries or execute code on the system. Additionally, privileged API operators should be unable to perform TCP connections to arbitrary hosts in the environment OpenBao is executing within. The API-driven audit subsystem granted privileged API operators the ability to do both with an attacker-controlled log prefix. Access to these endpoints should be restricted.

### Patches

OpenBao v2.3.2 will patch this issue.

### Workarounds

Users may deny all access to the `sys/audit/*` interface (with `create` and `update`) permission via policies with explicit deny grants. This would not restrict `root` level operators, however, for whom there are no workarounds. 

This interface allowed arbitrary filesystem and network (write) access as the user the OpenBao server was running as; in conjunction with allowing custom plugins or other system processes this may enable code execution.

### References

This issue was disclosed to HashiCorp and is the OpenBao equivalent of the following tickets:

- https://discuss.hashicorp.com/t/hcsec-2025-14-privileged-vault-operator-may-execute-code-on-the-underlying-host/76033
- https://nvd.nist.gov/vuln/detail/CVE-2025-6000

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-xp75-r577-cvhp
- https://nvd.nist.gov/vuln/detail/CVE-2025-54997
- https://nvd.nist.gov/vuln/detail/CVE-2025-6000
- https://github.com/openbao/openbao/pull/1634
- https://github.com/openbao/openbao/commit/a14053c9679d6e9cf370f00cf933476cda6d84a2
- https://discuss.hashicorp.com/t/hcsec-2025-14-privileged-vault-operator-may-execute-code-on-the-underlying-host/76033
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.3.2
