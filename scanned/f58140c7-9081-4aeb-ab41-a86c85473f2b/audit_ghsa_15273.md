# [H] soft-serve vulnerable to arbitrary code execution by crafting git-lfs requests

## Summary
Severity: High
Advisory: GHSA-m445-w3xr-vp2f
CVE: CVE-2024-41956
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-02
Source: https://github.com/advisories/GHSA-m445-w3xr-vp2f
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0 <0.7.5

## Details
### Impact
Any servers using soft-serve server and git

### Patches
>0.7.5

### Workarounds
None.

### References
n/a.

---

It is possible for a user who can commit files to a repository hosted by Soft Serve to execute arbitrary code via environment manipulation and Git.

The issue is that Soft Serve passes all environment variables given by the client to git subprocesses. This includes environment variables that control program execution, such as `LD_PRELOAD`.

This can be exploited to execute arbitrary code by, for example, uploading a malicious shared object file to Soft Serve via Git LFS (uploading it via LFS ensures that it is not compressed on disk and easier to work with). The file will be stored under its SHA256 hash, so it has a predictable name.

This file can then be referenced in `LD_PRELOAD` via a Soft Serve SSH session that causes git to be invoked. For example:

```bash
LD_PRELOAD=/.../data/lfs/1/objects/a2/b5/a2b585befededf5f95363d06d83655229e393b1b45f76d9f989a336668665a2f ssh server git-upload-pack repo
```

The example LFS file patches a shared library function called by git to execute a shell.

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-m445-w3xr-vp2f
- https://nvd.nist.gov/vuln/detail/CVE-2024-41956
- https://github.com/charmbracelet/soft-serve/commit/4daebdd422a6ba8c04162d023f8be355a8fe3184
- https://github.com/charmbracelet/soft-serve
- https://pkg.go.dev/vuln/GO-2024-3019
