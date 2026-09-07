# [C] motionEye: LFI → pass‑the‑hash admin → unsafe restore → unauth action exec (RCE)

## Summary
Severity: Critical
Advisory: GHSA-qxvg-h7q2-hcxh
CWE: CWE-22, CWE-269, CWE-306, CWE-347, CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-qxvg-h7q2-hcxh
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0 <0.44.0

## Details
## Summary
A multi‑stage chain in motionEye leads to remote code execution. The chain combines:

1. **Arbitrary file read (LFI)** via the picture download endpoint for **local motion cameras** using absolute paths.
2. **Pass‑the‑hash admin auth** due to accepting request signatures computed with password hashes.
3. **Unsafe config restore** that extracts attacker‑controlled tarballs into `CONF_PATH`.
4. **Unauthenticated action execution** via `/action/<id>/<action>`.

If the **normal user password is unset**, the chain becomes **unauthenticated RCE**. If a normal password exists, a **normal user** can still achieve **admin escalation and RCE**.

---

## Affected Code (motionEye repo)

### 1) LFI (absolute path) — `picture/<id>/download`
**Files:**
- `motioneye/motioneye/handlers/picture.py` → `download()` (local motion camera branch)
- `motioneye/motioneye/mediafiles.py` → `get_media_content()`

**Issue:** `get_media_content()` only blocks `..` and then joins `target_dir` with `path`. Absolute paths (e.g. `/etc/hosts`) bypass the join and are read directly.

### 2) Pass‑the‑hash admin auth
**File:** `motioneye/motioneye/handlers/base.py` → `get_current_user()`

**Issue:** The signature check allows signatures computed using the **admin password hash** (SHA1) as the key. If the hash is leaked (via LFI), admin access can be obtained without the plaintext password.

### 3) Unsafe restore (tar extraction)
**File:** `motioneye/motioneye/config.py` → `restore()`

**Issue:** `tar zxC CONF_PATH` is used on user‑supplied data without sanitizing entries. A crafted tar can drop executable files into `CONF_PATH`.

### 4) Unauthenticated action execution
**File:** `motioneye/motioneye/handlers/action.py` → `post()`

**Issue:** No authentication decorator is present. It executes `<action>_<camera_id>` found in `CONF_PATH` with `subprocess.Popen`.

---

## Exploit Chain (Detailed)

1. **Create or find a local motion camera id** (local motion cameras are required for the vulnerable LFI path).
2. **LFI via picture download**:
   - Request: `/picture/<id>/download/<absolute_path>`
   - Example: `/picture/1/download/%2Fetc%2Fhosts`
   - Result: Arbitrary file read.
3. **Read admin hash** from `/etc/motioneye/motion.conf`:
   - Contains `@admin_password <SHA1_HASH>`.
4. **Pass‑the‑hash admin**:
   - Compute signature for `/config/restore?_username=admin` using the **hash** as key.
   - Admin access is accepted with hash‑based signatures.
5. **Restore malicious tar**:
   - Upload a tar containing `lock_<id>` (or any action) as an executable.
   - File is written into `CONF_PATH` by restore.
6. **Trigger unauth action**:
   - POST `/action/<id>/lock`
   - The server executes the injected file.

---

## Proof of Execution (Observed Output)
In local testing, the injected action created a marker file:

```
/tmp/meye_rce_ok
```

Verification command:
```
docker exec -it motioneye ls -la /tmp | grep meye_rce_ok
```
Example output:
```
-rw-r--r-- 1 root root 0 ... /tmp/meye_rce_ok
```

---

## Preconditions / Requirements

- At least **one local motion camera** exists (e.g., `netcam_url`, `videodevice`).
- `picture/<id>/download` is reachable:
  - **Unauth** if `@normal_password` is empty (default in some installs).
  - **Auth required** if normal password is set (attacker needs normal creds).

---

## Impact
- **Unauth RCE** (normal password unset).
- **Authenticated RCE** (normal user → admin → RCE).
- Arbitrary file read on server filesystem.
- Full compromise of motionEye process account.

---

## Suggested Fixes
1. **Block absolute paths** in `get_media_content()` and `get_media_path()`.
2. **Remove hash‑based signature acceptance**; only accept signatures computed with plaintext passwords.
3. **Harden restore**: reject absolute paths, `..`, symlinks, non‑regular files.
4. **Require authentication** on `ActionHandler` (admin‑only).

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-qxvg-h7q2-hcxh
- https://github.com/motioneye-project/motioneye
