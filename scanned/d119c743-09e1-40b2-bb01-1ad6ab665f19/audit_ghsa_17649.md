# [C] Gogs allows deletion of internal files which leads to remote command execution

## Summary
Severity: Critical
Advisory: GHSA-wj44-9vcg-wjq7
CVE: CVE-2024-56731
CWE: CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-24
Source: https://github.com/advisories/GHSA-wj44-9vcg-wjq7
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.3

## Details
### Summary
Due to the insufficient patch for the CVE-2024-39931, it's still possible to delete files under the `.git` directory and achieve remote command execution.

### Details
In the patch for CVE-2024-39931, the following check is added:
https://github.com/gogs/gogs/commit/77a4a945ae9a87f77e392e9066b560edb71b5de9

```diff
+	// 🚨 SECURITY: Prevent uploading files into the ".git" directory
+	if isRepositoryGitPath(opts.TreePath) {
+		return errors.Errorf("bad tree path %q", opts.TreePath)
+	}
```


While the above code snippet checks if the specified path is a `.git` directory, there are no checks for symbolic links in the later steps. So, by creating a symbolic link that points to the `.git` directory, an attacker can still delete arbitrary files in the `.git` directory and achieve remote command execution.

### Impact
Unprivileged user accounts can execute arbitrary commands on the Gogs instance with the privileges of the account specified by `RUN_USER` in the configuration. It allows attackers to access and alter any users' code hosted on the same instance.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-wj44-9vcg-wjq7
- https://nvd.nist.gov/vuln/detail/CVE-2024-56731
- https://github.com/gogs/gogs/commit/77a4a945ae9a87f77e392e9066b560edb71b5de9
- https://github.com/advisories/GHSA-ccqv-43vm-4f3w
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.13.3
