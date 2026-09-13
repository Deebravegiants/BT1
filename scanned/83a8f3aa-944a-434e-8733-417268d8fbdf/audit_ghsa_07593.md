# [M] Gogs has arbitrary file read/write via Path Traversal in Git hook editing

## Summary
Severity: Medium
Advisory: GHSA-mrph-w4hh-gx3g
CVE: CVE-2026-23633
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-mrph-w4hh-gx3g
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.4

## Details
## Vulnerability Description

In the endpoint:

```
/username/reponame/settings/hooks/git/:name
```

the `:name` parameter:

* Is URL-decoded by **macaron routing**, allowing decoded slashes (`/`)
* Is then passed directly to:

```go
git.Repository.Hook("custom_hooks", name)
```

which internally resolves the path as:

```go
filepath.Join(repoPath, "custom_hooks", name)
```

Because no path sanitization is applied, supplying `../` sequences allows access to **arbitrary paths outside the repository**.

### As a Result:

* **GET:** Arbitrary file contents are displayed in the hook edit page textarea (**Local File Inclusion**).
* **POST:** Existing files can be overwritten with attacker-controlled content (**Arbitrary File Write**).

---

## Attack Prerequisites

* The attacker is an authenticated user
* The attacker has **Admin or higher privileges** on the target repository
* The attacker has the **AllowGitHook** permission (or is a site administrator)
* The target file is readable/writable by the **Gogs process OS permissions**

---

## Attack Scenario

1. An attacker (with AllowGitHook + repository Admin privileges) accesses the Git hook edit URL
2. A path containing `../` is supplied in `:name`, fully URL-encoded using `%2f`
3. The server resolves `custom_hooks/../../...` without validation
4. Arbitrary file contents are displayed and existing files can be overwritten

---

## Potential Impact

* **Sensitive information disclosure:** `app.ini`, databases, logs, environment variables, etc.
* **Configuration or data tampering:** Overwriting existing files
* **Secondary impact:** Extraction of `SECRET_KEY` and database credentials may allow token forging or further compromise

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-mrph-w4hh-gx3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-23633
- https://github.com/gogs/gogs/commit/4894629903f9508fe85567c44f68804f008f1655
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.13.4
