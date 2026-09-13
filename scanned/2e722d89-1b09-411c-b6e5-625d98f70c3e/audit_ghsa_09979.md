# [M] Sync-in Server has Username Enumeration via Timing Attack

## Summary
Severity: Medium
Advisory: GHSA-43fj-qp3h-hrh5
CVE: CVE-2026-41161
CWE: CWE-208
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-43fj-qp3h-hrh5
Type: github-advisory

## Affected
- npm: `@sync-in/server` — affected >=0 <2.2.0

## Details
### Summary
The `/api/auth/login` endpoint contains a logic flaw that allows unauthenticated remote attackers to enumerate valid usernames by measuring the application's response time.

### Details
The logic flaw can be located at the below point in source:
https://github.com/Sync-in/server/blob/7868bb2b3025f92e6c38087456304758713971b2/backend/src/applications/users/services/users-queries.service.ts#L91-L95

Endpoints used for authentication should respond to the user with a consistent cadence, preventing remote actors from deriving sensitive information about an application based on backend behavior. In the case of authentication endpoints, this timing discrepancy is often caused by short-circuiting due to the lack of a matched user to compare against - as is the case with Sync-in.

### Validation
TickTock Enum (Burp Suite Extension) was utilized to validate this finding. Authentication attempts with a valid username see a response from the application at around 350-400ms on average, while invalid usernames are returned at only 95-100ms on average.
<img width="1302" height="284" alt="image" src="https://github.com/user-attachments/assets/31eeb72a-c3c2-4057-ac69-c0c92f0bbd4e" />

### Impact
An unauthenticated remote attacker can enumerate valid usernames. This significantly weakens the application's security posture by facilitating targeted brute-force attacks, stuffing, social engineering, and a suite of other more targeted attacks.

## References
- https://github.com/Sync-in/server/security/advisories/GHSA-43fj-qp3h-hrh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-41161
- https://github.com/Sync-in/server
- https://github.com/Sync-in/server/releases/tag/v2.2.0
