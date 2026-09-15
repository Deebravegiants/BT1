# [M] Yamcs has No Rate Limiting on Authentication Endpoint

## Summary
Severity: Medium
Advisory: GHSA-w5r6-mcgq-7pq4
CVE: CVE-2026-44596
CWE: CWE-307
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-w5r6-mcgq-7pq4
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.7

## Details
### Summary

The authentication endpoint `POST /auth/token` in `yamcs-core` lacks any form of rate limiting, account lockout, or failed attempt throttling. As a result, an unauthenticated remote attacker can perform unlimited password guessing attempts against any user account.

This missing rate limiting vulnerability (CWE-307) significantly increases the risk of successful brute-force attacks.

### Root Cause

**File:** `yamcs-core/src/main/java/org/yamcs/http/auth/AuthHandler.java`

`POST /auth/token` has no rate limiting, no lockout after failed attempts, and no CAPTCHA. The handler processes unlimited authentication requests without any throttling mechanism:

```java
// AuthHandler.java — handleToken()
// No throttle, no failed attempt counter, no lockout
private void handleToken(HandlerContext ctx) {
    ...
    getSecurityStore().login(token).whenComplete((info, err) -> {
        // Directly attempts authentication with no rate check
    });
}
```

This is absent by default — the official quickstart and documentation contain no guidance on configuring rate limiting.

### Impact

An attacker can make unlimited authentication attempts against any account. This enables efficient brute-force attacks against any account.

### Proof of Concept

```bash
# 20 attempts — zero rate limiting
for i in $(seq 1 20); do
  curl -s -o /dev/null -w "Attempt $i: HTTP %{http_code}\n" \
    -X POST "http://TARGET:8090/auth/token" \
    -d "grant_type=password&username=operator&password=operator12$i"
done
# All return HTTP 401 — no HTTP 429 ever
```

**Confirmed:** 20 attempts in 0.07 seconds, no rate limiting enforced.

### Fix

Implement DRF-style throttling on `/auth/token`:

```java
// Track failed attempts per IP
private static final Cache<String, Integer> FAILED_ATTEMPTS =
    CacheBuilder.newBuilder().expireAfterWrite(15, TimeUnit.MINUTES).build();

private static final int MAX_ATTEMPTS = 10;

private void handleToken(HandlerContext ctx) {
    String ip = ctx.getRemoteAddress();
    int attempts = Optional.ofNullable(FAILED_ATTEMPTS.getIfPresent(ip)).orElse(0);
    if (attempts >= MAX_ATTEMPTS) {
        throw new TooManyRequestsException("Rate limit exceeded");
    }
    // ... existing auth logic
    // On failure: FAILED_ATTEMPTS.put(ip, attempts + 1)
}
```

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-w5r6-mcgq-7pq4
- https://github.com/yamcs/yamcs
