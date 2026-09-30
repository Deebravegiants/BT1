# [M] motionEye's World-Readable Configuration File Exposes Admin Password Hash

## Summary
Severity: Medium
Advisory: GHSA-rhgp-6wq6-9j67
CVE: CVE-2026-32315
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-rhgp-6wq6-9j67
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0 <0.44.0

## Details
# Security Advisory: World-Readable Configuration File Exposes Admin Password Hash in motionEye

## Summary

motionEye v0.43.1 and prior versions create the configuration file `/etc/motioneye/motion.conf` with `644` permissions (`-rw-r--r--`), making it readable by any local user on the system. This file contains sensitive data including the admin password hash, which can be leveraged by other vulnerabilities to escalate privileges.

## Affected Versions

- motionEye <= 0.43.1b4
- Fixed in motionEye 0.44.0b1 (applies `0600` mode to `motion.conf` and `camera-*.conf` files)

## Vulnerability Details

### World-Readable Configuration File (CWE-732)

When motionEye writes its configuration, the file `/etc/motioneye/motion.conf` is created with `644` permissions regardless of the installation method. This file contains the admin password hash in the `@admin_password` field:

```
# @admin_username admin
# @admin_password c18006fc138809314751cd1991f1e0b820fabd37
```

Any local user can read this hash without elevated privileges:

```bash
$ sudo -u testuser cat /etc/motioneye/motion.conf
# @admin_password c18006fc138809314751cd1991f1e0b820fabd37
```

Additionally, per-camera configuration files (`camera-*.conf`) are also created with the same `644` permissions, potentially exposing camera-specific credentials and settings.

## Impact

The exposed admin password hash enables several attack paths:

- **Offline password cracking:** The SHA1 hash can be cracked to recover the plaintext admin password
- **Authentication bypass:** When combined with the signature authentication weakness (see GHSA-45h7-499j-7ww3), the hash can be used directly to forge authenticated admin API requests
- **Full system compromise:** When further chained with CVE-2025-60787 (OS command injection), a local unprivileged user can escalate to the Motion daemon user (often root)

## Proof of Concept

The following demonstrates that an unprivileged user can read the admin password hash from the config file and verify it matches the admin's password:

```bash
# Verify the file permissions
$ ls -la /etc/motioneye/motion.conf
-rw-r--r-- 1 motion motion 255 Mar 11 15:42 /etc/motioneye/motion.conf

# Read the hash as an unprivileged user
$ sudo -u testuser cat /etc/motioneye/motion.conf | grep admin_password
# @admin_password c18006fc138809314751cd1991f1e0b820fabd37

# Verify the hash matches the admin password (SHA1)
$ sudo -u testuser python3 -c "import hashlib; print(hashlib.sha1(b'testpassword123').hexdigest())"
c18006fc138809314751cd1991f1e0b820fabd37
```

### Verified Output

The following output was captured on a fresh motionEye v0.43.1b4 installation (official `motioneye_init` method, admin password set to `testpassword123`):

```
$ ls -la /etc/motioneye/motion.conf
-rw-r--r-- 1 motion motion 255 Mar 11 15:42 /etc/motioneye/motion.conf

$ sudo -u testuser cat /etc/motioneye/motion.conf | grep admin_password
# @admin_password c18006fc138809314751cd1991f1e0b820fabd37

$ sudo -u testuser python3 -c "import hashlib; print(hashlib.sha1(b'testpassword123').hexdigest())"
c18006fc138809314751cd1991f1e0b820fabd37
```

The hash extracted by the unprivileged `testuser` matches the SHA1 of the admin password, confirming full credential exposure.

## Reproduction Steps

This vulnerability has been tested and confirmed with both installation methods described in the official motionEye documentation.

### Method 1: Manual Installation

1. Install motionEye on a Linux system:
   ```bash
   sudo pip install motioneye
   mkdir -p /etc/motioneye /var/log/motioneye /var/lib/motioneye /run/motioneye
   cp /usr/local/lib/python3.12/dist-packages/motioneye/extra/motioneye.conf.sample /etc/motioneye/motioneye.conf
   sudo meyectl startserver -c /etc/motioneye/motioneye.conf
   ```

2. Set an admin password via the web UI at `http://localhost:8765`

3. Verify the config file is world-readable:
   ```bash
   ls -la /etc/motioneye/motion.conf
   # -rw-r--r-- 1 root root 255 ... /etc/motioneye/motion.conf
   ```

4. As an unprivileged user, read the hash:
   ```bash
   sudo -u testuser cat /etc/motioneye/motion.conf
   # @admin_password c18006fc138809314751cd1991f1e0b820fabd37
   ```

### Method 2: Official `motioneye_init` Installation

1. Install motionEye using the official init script:
   ```bash
   sudo pip install motioneye
   sudo motioneye_init
   ```

2. The `motioneye_init` script automatically creates the required directories, installs the systemd service, and starts motionEye. Set an admin password via the web UI at `http://localhost:8765`

3. Verify the config file is still world-readable:
   ```bash
   ls -la /etc/motioneye/motion.conf
   # -rw-r--r-- 1 motion motion 255 ... /etc/motioneye/motion.conf
   ```

   Note that while the ownership changes to `motion:motion` (instead of `root:root` in the manual method), the permissions remain `644`, meaning any local user can still read the file.

4. Confirm as an unprivileged user:
   ```bash
   sudo -u testuser cat /etc/motioneye/motion.conf
   # @admin_password c18006fc138809314751cd1991f1e0b820fabd37
   ```

Both installation methods produce the same vulnerable state, confirming this is the default behavior of the software and not a user misconfiguration.

## Related Vulnerabilities

- **GHSA-45h7-499j-7ww3:** Password hash accepted as API signing key (CWE-836), which allows the hash exposed by this vulnerability to be used for forging authenticated admin API requests
- **CVE-2025-60787:** OS command injection via `image_file_name`, which requires admin authentication. When chained with both this vulnerability and GHSA-45h7-499j-7ww3, enables local privilege escalation to root

## Suggested Remediation

1. **Fix file permissions:** Create `motion.conf` and `camera-*.conf` with `600` permissions (`-rw-------`), readable only by the motionEye service user (addressed in motionEye 0.44.0b1)

## Timeline

- **2026-03-11:** Vulnerability discovered during security research
- **2026-03-11:** Vendor notified via GitHub Security Advisory
- **2026-03-12:** Vendor acknowledged, confirmed fix in motionEye 0.44.0b1

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-rhgp-6wq6-9j67
- https://github.com/motioneye-project/motioneye
