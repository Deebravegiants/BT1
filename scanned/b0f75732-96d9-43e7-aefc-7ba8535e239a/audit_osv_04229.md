# [C] authentik vulnerable to password authentication bypass via X-Forwarded-For HTTP header

## Summary
Severity: Critical
Advisory: BIT-authentik-2024-47070
Aliases: CVE-2024-47070, GHSA-7jxf-mmg9-9hg7
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2024-47070
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2024.8.0 <2024.8.3

## Details
authentik is an open-source identity provider. A vulnerability that exists in versions prior to 2024.8.3 and 2024.6.5 allows bypassing password login by adding X-Forwarded-For header with an unparsable IP address, e.g. `a`. This results in a possibility of logging into any account with a known login or email address. The vulnerability requires the authentik instance to trust X-Forwarded-For header provided by the attacker, thus it is not reproducible from external hosts on a properly configured environment.  The issue occurs due to the password stage having a policy bound to it, which skips the password stage if the Identification stage is setup to also contain a password stage. Due to the invalid X-Forwarded-For header, which does not get validated to be an IP Address early enough, the exception happens later and the policy fails. The default blueprint doesn't correctly set `failure_result` to `True` on the policy binding meaning that due to this exception the policy returns false and the password stage is skipped. Versions 2024.8.3 and 2024.6.5 fix this issue.

## References
- https://github.com/goauthentik/authentik/commit/78f7b04d5a62b2a9d4316282a713c2c7857dbe29
- https://github.com/goauthentik/authentik/commit/dd8f809161e738b25765797eb2a5c77a7d3fc2cf
- https://github.com/goauthentik/authentik/security/advisories/GHSA-7jxf-mmg9-9hg7
- https://nvd.nist.gov/vuln/detail/CVE-2024-47070
