# [H]  Romeo is vulnerable to Archive Slip due to missing checks in sanitization

## Summary
Severity: High
Advisory: GHSA-p799-g7vv-f279
CVE: CVE-2026-32805
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:L/SA:L (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-p799-g7vv-f279
Type: github-advisory

## Affected
- Go: `github.com/ctfer-io/romeo/webserver` — affected >=0 <0.2.2

## Details
## Summary

The `sanitizeArchivePath` function in `webserver/api/v1/decoder.go` (lines 80-88) is vulnerable to a path traversal bypass due to a missing trailing path separator in the `strings.HasPrefix` check. A crafted tar archive can write files outside the intended destination directory.

## Vulnerable Code

File: `webserver/api/v1/decoder.go`, lines 80-88

```go
func sanitizeArchivePath(d, t string) (v string, err error) {
	v = filepath.Join(d, t)
	if strings.HasPrefix(v, filepath.Clean(d)) {
		return v, nil
	}
	return "", &ErrPathTainted{
		Path: t,
	}
}
```

The function is called at line 48 inside `[*Decompressor].Unzip`, which is invoked by `Decode` (line 80) during execution of the webserver CLI (command `download`).

## Root Cause

`strings.HasPrefix(v, filepath.Clean(d))` does not append a trailing `/` to the directory prefix, causing a **directory name prefix collision**. If the destination is `/home/user/extract-output` and a tar entry is named `../extract-outputevil/pwned`, the joined path `/home/user/extract-outputevil/pwned` passes the prefix check — it starts with `/home/user/extract-output` — even though it is entirely outside the intended directory.

## Steps to Reproduce

1. **Deploy Romeo**. A measured app writes its coverage data.

2. **Place the PoC zip on the PVC.** Any pod with write access to the `ReadWriteMany` PVC (or the webserver itself) copies a `poc-path-traversal.tar` into the `coverdir` mount path. The archive contains legitimate coverage files alongside two crafted entries with path-traversal names.

3. **Run the webserver CLI against the running webserver:**
   ```
   webserver download \
     --server http://localhost:8080 \
     --directory /home/user/extract-output
   ```

4. **Observe the bypass.** `unzip` processes the zip stream. For the malicious entries:
   ```
   // entry name: ../extract-outputevil/poc-proof.txt
   filepath.Join("/home/user/extract-output", "../extract-outputevil/poc-proof.txt")
     => "/home/user/extract-outputevil/poc-proof.txt"

   strings.HasPrefix("/home/user/extract-outputevil/poc-proof.txt",
                     "/home/user/extract-output")
     => true   // BUG: prefix collision; file lands OUTSIDE target dir
   ```
   Both malicious entries are written outside `/home/user/extract-output/`. The legitimate coverage files land correctly inside it.

## Impact

Successful exploitation gives an attacker arbitrary file write on the machine running the webserver CLI. Real-world primitives include:

- Overwriting `~/.bashrc` / `~/.zshrc` / `~/.profile` for RCE on next shell login
- Appending to `~/.ssh/authorized_keys` for persistent SSH backdoor
- Dropping a malicious entry into `~/.kube/config` to hijack cluster access
- Writing crontab entries for persistent scheduled execution

The attack surface is widened by the default `ReadWriteMany` PVC access mode, which means any pod in the cluster with the PVC mounted can inject the payload — not just the Romeo webserver itself.

## References
- https://github.com/ctfer-io/romeo/security/advisories/GHSA-p799-g7vv-f279
- https://nvd.nist.gov/vuln/detail/CVE-2026-32805
- https://github.com/ctfer-io/romeo/commit/c2ebcfb9f305fd5f6ef68858de82507dbac10263
- https://github.com/ctfer-io/romeo
