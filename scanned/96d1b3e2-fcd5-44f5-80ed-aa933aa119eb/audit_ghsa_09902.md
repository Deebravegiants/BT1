# [M] File Browser has an access rule bypass via HasPrefix without trailing separator in path matching

## Summary
Severity: Medium
Advisory: GHSA-5q48-q4fm-g3m6
CVE: CVE-2026-35605
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-5q48-q4fm-g3m6
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.1

## Details
Hi,

The `Matches()` function in `rules/rules.go` uses `strings.HasPrefix()` without a trailing directory separator when matching paths against access rules. A rule for `/uploads` also matches `/uploads_backup/`, granting or denying access to unintended directories. Verified against v2.62.2 (commit 860c19d).

## Details

At `rules/rules.go:29-35`:

    func (r *Rule) Matches(path string) bool {
        if r.Regex {
            return r.Regexp.MatchString(path)
        }
        return strings.HasPrefix(path, r.Path)
    }

When a rule has `Path: "/uploads"`, any path starting with `/uploads` matches, including `/uploads_backup/secret.txt`. The regex variant at line 31 uses proper matching, but the non-regex path uses a prefix check without ensuring the match ends at a directory boundary.

The `Check()` function at `http/data.go:29-48` iterates all rules with last-match-wins semantics. No secondary validation exists beyond this prefix check.

## PoC

Admin configures: allow rule `Path: "/shared"` for a restricted user.

Filesystem contains:
- `/shared/` (intended to be accessible)
- `/shared_private/` (intended to be restricted)

User requests `/shared_private/secret.txt`:
- `strings.HasPrefix("/shared_private/secret.txt", "/shared")` returns true
- Allow rule applies
- Access granted to the unintended directory

## Impact

Authenticated users can access files in sibling directories that share a common prefix with an allowed directory, bypassing the admin's intended access configuration.

## Prior art

Prior advisories GHSA-4mh3-h929-w968 (path-based access control bypass) and GHSA-9f3r-2vgw-m8xp (path traversal in copy/rename) addressed related access control issues. This HasPrefix prefix-collision is a distinct, unreported variant.

## Suggested Fix

    func (r *Rule) Matches(path string) bool {
        if r.Regex {
            return r.Regexp.MatchString(path)
        }
        prefix := r.Path
        if prefix != "/" && !strings.HasSuffix(prefix, "/") {
            prefix += "/"
        }
        return path == r.Path || strings.HasPrefix(path, prefix)
    }

Koda Reef

---

**Update:** Fix submitted as PR #5889.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-5q48-q4fm-g3m6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35605
- https://github.com/filebrowser/filebrowser/pull/5889
- https://github.com/filebrowser/filebrowser
