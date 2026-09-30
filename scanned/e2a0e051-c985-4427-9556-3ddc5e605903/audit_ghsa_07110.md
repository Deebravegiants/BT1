# [M] Open WebUI: Account enumeration via observable login timing discrepancy

## Summary
Severity: Medium
Advisory: GHSA-7rw5-9f7q-xj36
CVE: CVE-2026-59218
CWE: CWE-208
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-7rw5-9f7q-xj36
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.10.0

## Details
### Summary

The `/api/v1/auths/signin` endpoint leaked whether an email address belonged to a registered account through a response-time side channel. Password verification ran bcrypt only when the email was found in the database; for a non-existent email the request returned early without hashing. The expensive bcrypt comparison therefore made valid-account attempts respond significantly slower (~180 ms) than non-existent ones (~5 ms), so an unauthenticated attacker could enumerate valid accounts by measuring response time.

### Details

On signin the backend looked the user up by email and only performed the bcrypt password comparison if a record existed. A missing email short-circuited before any hashing, producing the timing gap. The built-in brute-force throttling did not prevent it: sending one request at a time with a small delay between requests stays under the rate limit while still exposing the difference.

Observed in the reporter's run (HTTP 400 for every attempt, the response time is the signal):

```
Email                Status   Response time
joe@example.com      400      186 ms   <- valid account
larry@example.com    400        9 ms
jose@example.com     400        6 ms
james@example.com    400        5 ms
```

### Impact

An unauthenticated attacker can enumerate which email addresses are registered accounts, which enables targeted password-spraying against confirmed accounts. The impact is amplified by MFA not being enabled by default. No data is read or modified; the disclosure is limited to account existence.

### Patched

The authentication path now runs a bcrypt verification against a constant placeholder hash whenever the email does not resolve to an active credential, so a real hash comparison executes on every attempt and the response time is the same whether or not the account exists. Fixed in 0.10.0.

### Credits

@dievus

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-7rw5-9f7q-xj36
- https://nvd.nist.gov/vuln/detail/CVE-2026-59218
- https://github.com/open-webui/open-webui/pull/26385
- https://github.com/open-webui/open-webui/commit/993e74912199c66c522f08ec81abe31d76985e39
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
