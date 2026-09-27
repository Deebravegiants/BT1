# [H] Nginx-UI: Unauthenticated First-Run Installer Allows Remote Initial Admin Claim

## Summary
Severity: High
Advisory: GHSA-h27v-ph7w-m9fp
CVE: CVE-2026-42221
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-h27v-ph7w-m9fp
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=2.0.0 <2.3.8

## Details
### Summary
An unauthenticated network attacker can claim the initial administrator account on a fresh `nginx-ui` instance during the first-run setup window. The public `/api/install` endpoint is reachable without authentication, and the request-encryption flow only protects payload confidentiality in transit; it does not authenticate who is allowed to perform installation. A remote attacker who reaches the service before the legitimate operator can set the admin email, username, and password, causing permanent initial-instance takeover.

### Details
The vulnerable route is exposed publicly through the main API router. `router/routers.go:61-70` mounts `system.InitPublicRouter(root)` under `/api`, and `api/system/router.go:16-19` registers both `GET /api/install` and `POST /api/install` without `AuthRequired()`.

The install handler only checks whether the instance is already installed and whether more than ten minutes have elapsed since startup. `api/system/install.go:26-33` treats the instance as uninstalled when `JwtSecret` is empty and `SkipInstallation` is false. `api/system/install.go:56-69` rejects requests only if installation has already happened or the ten-minute window has expired.

If those checks pass, the unauthenticated caller controls the initialization flow. `api/system/install.go:77-81` generates and saves the JWT secret, node secret, and certificate email from attacker-controlled input, and `api/system/install.go:93-97` overwrites user ID `1` with the attacker-chosen username and password hash. `internal/kernel/init_user.go:15-22` guarantees that privileged user ID `1` exists ahead of time, so there is always an account to claim.

The public-key bootstrap does not add authentication. `api/crypto/router.go:5-9` exposes `POST /api/crypto/public_key` publicly, `api/crypto/crypto.go:12-32` returns a server public key to any caller, `internal/crypto/crypto.go:44-61` stores a shared keypair in cache, and `internal/middleware/encrypted_params.go:25-50` only decrypts `encrypted_params` before passing the request to the install handler. No request ID, local-only restriction, bootstrap secret, or prior trust check is enforced.

This was verified locally in an isolated lab instance. A fresh instance returned `{"lock":false,"timeout":false}`, an unauthenticated `POST /api/install` returned `{"message":"ok"}`, the instance then flipped to `{"lock":true,"timeout":false}`, and the on-disk SQLite database showed user ID `1` renamed to the attacker-controlled username with a non-empty password hash.

### PoC
The quickest local verification path is the helper script created during validation:

```bash
ATTACKER_EMAIL='attacker@example.com' ATTACKER_USER='attacker' ATTACKER_PASS='Password12345' \
'/Users/r1zzg0d/Documents/CVE hunting/targets/nginx-ui/output/verify/verify_fresh_install_takeover.sh'
```

Expected proof points:

```text
[1/6] Fresh-instance status:
{
  "lock": false,
  "timeout": false
}

[3/6] Claiming the initial administrator account...
{
  "message": "ok"
}

[4/6] Verifying install is now locked...
{
  "lock": true,
  "timeout": false
}

[5/6] Verifying the on-disk admin record was overwritten...
{
  "id": 1,
  "name": "attacker",
  "password_len": 60
}
```

To confirm the final state manually:

```bash
sqlite3 '/Users/r1zzg0d/Documents/CVE hunting/targets/nginx-ui/tmp/poc-install-takeover/database.db' \
'select id,name,length(password) from users where id=1;'
```

Expected output:

```text
1|attacker|60
```

Manual HTTP reproduction is also straightforward:

1. Request `GET /api/install` and confirm `lock=false` and `timeout=false`.
2. Request `POST /api/crypto/public_key` to obtain the public RSA key.
3. Encrypt `{"email":"attacker@example.com","username":"attacker","password":"Password12345"}` with that public key and base64-encode the ciphertext.
4. Submit the ciphertext to `POST /api/install` as `{"encrypted_params":"..."}`.
5. Re-request `GET /api/install` and observe that `lock=true`.
6. Inspect the backing database and confirm user ID `1` now belongs to the attacker-controlled username.

### Impact
This is an authentication bypass / initial admin claim vulnerability affecting fresh, uninitialized instances that are reachable over the network during the installation window. Any attacker able to reach the service before the legitimate operator can permanently take ownership of the first administrator account and thereby seize control of the application. Because `nginx-ui` is an administrative interface for Nginx and related host-management features, compromise of the initial admin account can lead to unauthorized configuration changes, certificate management abuse, backup manipulation, service disruption, and broader operational takeover of the managed environment.

### Remediation
1. Require a single-use bootstrap secret for installation. Generate the token locally on first start, print it only to the server console or write it to a root-owned local file, and require it on `POST /api/install`.
2. Restrict installation endpoints to loopback by default until setup completes. Remote setup should require an explicit opt-in configuration flag, not be enabled automatically on all interfaces.
3. Make installer claim atomic and explicitly stateful. Persist a dedicated installation state record, consume the bootstrap token exactly once, and refuse concurrent or repeated initialization attempts even within the startup window.

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-h27v-ph7w-m9fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-42221
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.8
