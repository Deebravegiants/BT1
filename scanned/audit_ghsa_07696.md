# [H] FrankenPHP's unicode case-folding length expansion causes incorrect split_path index (SCRIPT_NAME/PATH_INFO confusion) in FrankenPHP

## Summary
Severity: High
Advisory: GHSA-g966-83w7-6w38
CVE: CVE-2026-24895
CWE: CWE-180, CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-g966-83w7-6w38
Type: github-advisory

## Affected
- Go: `github.com/dunglas/frankenphp` — affected >=0 <1.11.2

## Details
### Summary

FrankenPHP’s CGI path splitting logic improperly handles Unicode characters during case conversion. The logic computes the split index (for finding `.php`) on a lowercased copy of the request path but applies that byte index to the original path.

Because `strings.ToLower()` in Go can increase the byte length of certain UTF-8 characters (e.g., `Ⱥ` expands when lowercased), the computed index may not align with the correct position in the original string. This results in an incorrect `SCRIPT_NAME` and `SCRIPT_FILENAME`, potentially causing FrankenPHP to execute a file other than the one intended by the URI.

### **Details**

The vulnerability resides in the `splitPos()` function and its usage within `splitCgiPath()`. The logic attempts to find the script extension (e.g., `.php`) in a case-insensitive manner by lowercasing the path:

```go
lowerPath := strings.ToLower(path)
idx := strings.Index(lowerPath, strings.ToLower(split))
return idx + len(split)
```

The issue is that the returned `idx` represents a byte offset within `lowerPath`. However, `splitCgiPath()` uses this index to slice the **original** `path`:

```go
fc.docURI = path[:splitPos]
fc.pathInfo = path[splitPos:]
fc.scriptName = strings.TrimSuffix(path, fc.pathInfo)
fc.scriptFilename = sanitizedPathJoin(fc.documentRoot, fc.scriptName)
```

This logic relies on the assumption that `len(strings.ToLower(path)) == len(path)`. This assumption is false for certain Unicode characters. For example, the character `Ⱥ` (U+023A) requires 2 bytes in UTF-8 (`0xC8 0xBA`), but its lowercase equivalent `ⱥ` (U+2C65) requires 3 bytes (`0xE2 0xB1 0xA5`).

If the path contains such characters before the `.php` extension, the index calculated on `lowerPath` will be larger than the corresponding visual point in the original `path`. When applied to the original path, the split occurs at the wrong byte offset. This can cause the server to treat a larger portion of the path as the script name, effectively allowing an attacker to manipulate `SCRIPT_FILENAME`.

### **PoC**

The following Go program demonstrates the discrepancy between the byte index in the lowercased string versus the original string.

1. Save the following as `poc.go`:

```go
package main

import (
    "fmt"
    "strings"
)

func splitPos(path string, split string) int {
    lowerPath := strings.ToLower(path)
    idx := strings.Index(lowerPath, strings.ToLower(split))
    if idx < 0 {
        return -1
    }
    return idx + len(split)
}

func main() {
    // U+023A: Ⱥ (UTF-8: C8 BA). Lowercase is ⱥ (UTF-8: E2 B1 A5), longer in bytes.
    // We construct a path where the byte expansion shifts the index.
    path := "/ȺȺȺȺshell.php.txt.php"
    split := ".php"

    pos := splitPos(path, split)

    fmt.Printf("orig bytes=%d\n", len(path))
    fmt.Printf("lower bytes=%d\n", len(strings.ToLower(path)))
    fmt.Printf("splitPos=%d\n", pos)

    // Current Unsafe Behavior:
    fmt.Printf("orig[:pos] (Calculated Script)=%q\n", path[:pos])
    fmt.Printf("orig[pos:] (Calculated PathInfo)=%q\n", path[pos:])

    // Expected Safe Behavior:
    want := strings.Index(path, split) + len(split)
    fmt.Printf("expected splitPos=%d\n", want)
    fmt.Printf("expected orig[:]=%q\n", path[:want])
}
```

2. Run the PoC:

```console
go run poc.go
```

3. **Output:**

```text
orig bytes=26
lower bytes=30
splitPos=22
orig[:pos]="/ȺȺȺȺshell.php.txt"
orig[pos:]=".php"
expected splitPos=18
expected orig[:]="/ȺȺȺȺshell.php"
```

In this example, FrankenPHP would identify `/ȺȺȺȺshell.php.txt` as the PHP script to execute, ignoring the fact that the actual file extension in the file system might be `.txt`.

### Impact*

This is a **Security Boundary Bypass** and **Path Confusion** vulnerability.

In setups where users can upload files (e.g., avatars, text files) that are stored within the document root or a reachable path, an attacker can upload a file containing malicious PHP code with a safe extension (e.g., `payload.txt`). By crafting a request with specific Unicode characters, the attacker can force FrankenPHP to calculate the `SCRIPT_FILENAME` as ending in `payload.txt`, while the request appears to contain `.php` to the internal router logic.

This results in the execution of non-PHP files as PHP scripts, leading to **Remote Code Execution (RCE)**.

### **Patched Versions**

* This issue is fixed in FrankenPHP version **1.11.2**.

### **Workarounds**

* Ensure that user-uploaded files are stored outside of the public document root.
* Implement strict WAF rules to reject requests containing specific multi-byte Unicode characters in the URL path if an upgrade is not immediately possible.

## References
- https://github.com/php/frankenphp/security/advisories/GHSA-g966-83w7-6w38
- https://nvd.nist.gov/vuln/detail/CVE-2026-24895
- https://github.com/php/frankenphp/commit/04fdc0c1e8fde94e2c1ad86217e962c88d27c53e
- https://github.com/php/frankenphp
- https://github.com/php/frankenphp/releases/tag/v1.11.2
