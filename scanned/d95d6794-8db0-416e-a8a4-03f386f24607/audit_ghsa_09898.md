# [H] Code Extension Marketplace: Zip Slip Path Traversal

## Summary
Severity: High
Advisory: GHSA-8x9r-hvwg-c55h
CVE: CVE-2026-35454
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-8x9r-hvwg-c55h
Type: github-advisory

## Affected
- Go: `github.com/coder/code-marketplace` — affected >=0 <1.2.3-0.20260402184705-988440dee05f

## Details
# Zip Slip Path Traversal in coder/code-marketplace

## Summary

A Zip Slip (CWE-22) vulnerability in `coder/code-marketplace` ≤ v2.4.1 allowed a malicious VSIX file to write arbitrary files outside the extension directory. `ExtractZip` passed raw zip entry names to a callback that wrote files via `filepath.Join` with no boundary check; `filepath.Join` resolved `..` components but did not prevent the result from escaping the base path.


## Root Cause

`ExtractZip` passed the raw, attacker-controlled `zf.Name` to a caller-supplied callback:

```go
return false, fn(zf.Name, zr)  // zf.Name not sanitized
```

`AddExtension` constructed the output path with `filepath.Join` and no boundary check:

```go
path := filepath.Join(dir, name)              // zip loop
path := filepath.Join(dir, file.RelativePath) // extra files loop
```

`filepath.Clean` resolved `..` lexically but did not confine the result to `dir`:

```
filepath.Join("/srv/ext/pub/1.0", "../../../../etc/cron.d/evil")
  → "/etc/cron.d/evil"
```

## Attack Scenario

An authenticated user (any upload-capable role) would submit a VSIX containing path-traversal entries.

On extraction, files would land at attacker-chosen paths writable by the marketplace process, enabling persistence (cron/init injection), SSH key injection, `ld.so.preload` hijacking, or binary overwrite depending on process privileges.

## Fix

Addressed in https://github.com/coder/code-marketplace/releases/tag/v2.4.2

## Recognition
Coder would like to thank [Kandlaguduru Vamsi](https://www.linkedin.com/in/vamsi-k-5419632a9/) for responsibly disclosing this issue in accordance with https://coder.com/security/policy

## References
- https://github.com/coder/code-marketplace/security/advisories/GHSA-8x9r-hvwg-c55h
- https://nvd.nist.gov/vuln/detail/CVE-2026-35454
- https://github.com/coder/code-marketplace/commit/988440dee05fceef8400ed725badc604dbf90792
- https://github.com/coder/code-marketplace
- https://github.com/coder/code-marketplace/releases/tag/v2.4.2
