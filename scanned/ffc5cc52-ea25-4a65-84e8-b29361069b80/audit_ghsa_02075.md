# [H] Hugo can execute a binary from the current directory on Windows

## Summary
Severity: High
Advisory: GHSA-8j34-9876-pvfq
CVE: CVE-2020-26284
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-8j34-9876-pvfq
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0 <0.79.1

## Details
## Impact

Hugo depends on Go's `os/exec` for certain features, e.g. for rendering of Pandoc documents if these binaries are found in the system `%PATH%` on Windows. However, if a malicious file with the same name (`exe` or `bat`) is found in the current working directory at the time of running `hugo`, the malicious command will be invoked instead of the system one.

Windows users who run `hugo` inside untrusted Hugo sites are affected.

## Patches
Users should upgrade to Hugo v0.79.1.

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-8j34-9876-pvfq
- https://nvd.nist.gov/vuln/detail/CVE-2020-26284
- https://github.com/golang/go/issues/38736
