# [M] Rucio WebUI has Username Enumeration via Login Error Message

## Summary
Severity: Medium
Advisory: GHSA-38wq-6q2w-hcf9
CVE: CVE-2026-25138
CWE: CWE-204
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-38wq-6q2w-hcf9
Type: github-advisory

## Affected
- PyPI: `rucio-webui` — affected >=0 <35.8.3
- PyPI: `rucio-webui` — affected >=36.0.0rc1 <38.5.4
- PyPI: `rucio-webui` — affected >=39.0.0rc1 <39.3.1

## Details
### Summary
The WebUI login endpoint returns distinct error messages depending on whether a supplied username exists, allowing unauthenticated attackers to enumerate valid usernames.

### Details
When submitting invalid credentials to `/ui/login`, the WebUI responds with different error messages based on the existence of the provided username (identity). A non-existent username results in an error indicating that no account is associated with the identity, while an existing username with an incorrect password produces a different authentication-related error.

This behavioral difference allows an attacker to distinguish valid usernames from invalid ones by observing the response content.

### Proof of Concept
**Bogus Login (Non-existent Username "15251087")**  
Response contains:
```
Cannot get find any account associated with 15251087 identity.
```

**Bogus Login (Existing Username "root", Wrong Password)**  
Response contains:
```
Cannot get auth token. It is possible that the presented identity root is not mapped to any Rucio account root.
```

The difference in error messages confirms whether a username exists.

### Impact
An unauthenticated attacker can enumerate valid usernames, which may be leveraged for targeted password guessing, credential stuffing, or social engineering attacks.

### Remediation / Mitigation
Return a generic authentication failure message for all login errors, regardless of whether the username exists. Avoid disclosing account or identity existence through error responses. Consider implementing rate limiting or additional login throttling to further reduce abuse.

#### Reources:
- OWASP Authentication Cheat Sheet -  Authentication and Error Messages: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#authentication-and-error-messages

## References
- https://github.com/rucio/rucio/security/advisories/GHSA-38wq-6q2w-hcf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25138
- https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#authentication-and-error-messages
- https://github.com/rucio/rucio
- https://github.com/rucio/rucio/releases/tag/35.8.3
- https://github.com/rucio/rucio/releases/tag/38.5.4
- https://github.com/rucio/rucio/releases/tag/39.3.1
