# [C] Wire-server vulnerable to Token Recipient Confusion resulting in account impersonation, deletion or malicious account creation

## Summary
Severity: Critical
Advisory: CVE-2022-31122
Aliases: GHSA-gq27-gmgq-fmxw
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-18
Source: https://osv.dev/vulnerability/CVE-2022-31122
Type: osv

## Details
Wire is an encrypted communication and collaboration platform. Versions prior to 2022-07-12/Chart 4.19.0 are subject to Token Recipient Confusion. If an attacker has certain details of SAML IdP metadata, and configures their own SAML on the same backend, the attacker can delete all SAML authenticated accounts of a targeted team, Authenticate as a user of the attacked team and create arbitrary accounts in the context of the team if it is not managed by SCIM. This issue is fixed in wire-server 2022-07-12 and is already deployed on all Wire managed services. On-premise instances of wire-server need to be updated to 2022-07-12/Chart 4.19.0, so that their backends are no longer affected. As a workaround, the risk of an attack can be reduced by disabling SAML configuration for teams (galley.config.settings.featureFlags.sso). Helm overrides are located in `values/wire-server/values.yaml` Note that the ability to configure SAML SSO as a team is disabled by default for on-premise installations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31122.json
- https://github.com/wireapp/wire-server/security/advisories/GHSA-gq27-gmgq-fmxw
- https://nvd.nist.gov/vuln/detail/CVE-2022-31122
