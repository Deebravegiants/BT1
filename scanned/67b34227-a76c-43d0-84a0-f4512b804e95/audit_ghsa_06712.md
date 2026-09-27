# [H] n8n: SSO Instance-Role Provisioning Allows Privilege Escalation to Instance Owner

## Summary
Severity: High
Advisory: GHSA-35q8-9mj6-wjmf
CVE: CVE-2026-65016
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-35q8-9mj6-wjmf
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.29.8

## Details
## Impact
n8n's Enterprise SSO instance-role provisioning maps a role claim asserted by the configured Identity Provider (IdP) to an n8n global role and applies it during authentication. The provisioning path did not prevent assignment of the `global:owner` role, unlike the token-exchange identity path, which explicitly rejects it. As a result, an SSO-authenticated user whose instance-role claim resolves to `global:owner` is provisioned as an instance owner, obtaining full administrative control over all workflows, credentials, users, and instance configuration.

This is a privilege-escalation issue that is exploitable only under specific conditions. It affects instances where Enterprise SSO is configured and instance-role provisioning is enabled via the `N8N_SSO_SCOPES_PROVISION_INSTANCE_ROLE` flag, which is disabled by default. Exploitation additionally requires the attacker to control the value of the instance-role claim issued by the IdP. As this claim is typically an administrator-managed attribute, exploitation generally requires control over the IdP or its claim-to-role mapping, or a permissive IdP configuration in which a lower-privileged user can influence the claim value. Deployments that do not use Enterprise SSO, or that have instance-role provisioning disabled, are not affected.

## Patches
The issue has been fixed in n8n versions 1.123.64, 2.29.8, and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable instance-role provisioning by unsetting or setting `N8N_SSO_SCOPES_PROVISION_INSTANCE_ROLE=false`.
- Audit IdP claim mappings to ensure no user-controllable attribute can supply the instance-role claim value.
- Restrict SSO access to fully trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-35q8-9mj6-wjmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-65016
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-privilege-escalation-via-sso-instance-role
