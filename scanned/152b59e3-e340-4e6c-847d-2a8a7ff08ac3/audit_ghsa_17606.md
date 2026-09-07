# [H] Graylog vulnerable to privilege escalation through API tokens

## Summary
Severity: High
Advisory: GHSA-3m86-c9x3-vwm9
CVE: CVE-2025-53106
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-3m86-c9x3-vwm9
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=6.2.0 <6.2.4
- Maven: `org.graylog2:graylog2-server` — affected >=6.3.0-alpha.1 <6.3.0-rc.2

## Details
### Impact

Graylog users can gain elevated privileges by creating and using API tokens for the local Administrator or any other user for whom the malicious user knows the ID.

For the attack to succeed, the attacker needs a user account in Graylog. They can then proceed to issue hand-crafted requests to the Graylog REST API and exploit a weak permission check for token creation.

### Workarounds

In Graylog version `6.2.0` and above, regular users can be restricted from creating API tokens. The respective configuration can be found in `System > Configuration > Users > "Allow users to create personal access tokens"`. This option should be *Disabled*, so that only administrators are allowed to create tokens.

### Recommended Actions

After upgrading Graylog from a vulnerable version to a patched version, administrators are advised to perform the following steps to ensure the integrity of their system:

#### Review API tokens 
An overview of all existing API tokens is available at `System > Users and Teams > Token Management`. Please review this list carefully and ensure each token is there for a reason.  

#### Check Audit Log (Graylog Enterprise only)
Graylog Enterprise provides an audit log that can be used to review which API tokens were created when the system was vulnerable. Please search the Audit Log for `action:create token` and match the *Actor* with the user for whom the token was created. In most cases this should be the same user, but there might be legitimate reasons for users to be allowed to create tokens for other users. If in doubt, please review the user's actual permissions.

#### Review API token creation requests
Graylog Open does not provide audit logging, but many setups contain infrastructure components, like reverse proxies, in front of the Graylog REST API. These components often provide HTTP access logs. Please check the access logs to detect malicious token creations by reviewing all API token requests to the `/api/users/{user_id}/tokens/{token_name}` endpoint (`{user_id}` and `{token_name}` may be arbitrary strings).

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-3m86-c9x3-vwm9
- https://nvd.nist.gov/vuln/detail/CVE-2025-53106
- https://github.com/Graylog2/graylog2-server/commit/6936bd16a783c2944a3d2f1e83902062520f90e3
- https://github.com/Graylog2/graylog2-server/commit/9215b8f1fd32566c31e6f7447ed864df3590c157
- https://github.com/Graylog2/graylog2-server
