# [H] Ory Keto has a SQL injection via forged pagination tokens

## Summary
Severity: High
Advisory: GHSA-c38g-mx2c-9wf2
CVE: CVE-2026-33505
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-c38g-mx2c-9wf2
Type: github-advisory

## Affected
- Go: `github.com/ory/keto` — affected >=0 <0.14.1-0.20260320140104-e4393662cd2e

## Details
## Description

The **GetRelationships API** in Ory Keto is vulnerable to SQL injection due to flaws in its pagination implementation.

Pagination tokens are encrypted using the secret configured in `secrets.pagination`. An attacker who knows this secret can craft their own tokens, including malicious tokens that lead to SQL injection. If this configuration value is not set, Keto falls back to a hard-coded default pagination encryption secret. Because this default value is publicly known, attackers can generate valid and malicious pagination tokens manually for installations where this secret is not set.

## Preconditions

This issue can be exploited when all of the following conditions are met:

- **GetRelationships API** is directly or indirectly accessible to the attacker
- The attacker can pass a raw pagination token to the affected API
- The configuration value `secrets.pagination` is not set or known to the attacker

## Impact

An attacker can execute arbitrary SQL queries through forged pagination tokens.

## Mitigation

As a first line of defense, **immediately** configure a custom value for `secrets.pagination` by generating a cryptographically secure random secret, for example:

```
openssl rand -base64 32
```

Next, upgrade **Keto** to a fixed version **as soon as possible**.

## References
- https://github.com/ory/keto/security/advisories/GHSA-c38g-mx2c-9wf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33505
- https://github.com/ory/keto
