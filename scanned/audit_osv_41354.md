# [M] repomix - Local File Inclusion via file:// URL Scheme in Git Clone Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-59703
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59703
Type: osv

## Details
repomix contains a local file inclusion vulnerability in the git clone endpoint that allows unauthenticated attackers to read arbitrary local git repositories. The isValidRemoteValue function in src/core/git/gitRemoteParse.ts fails to block file:// URLs, permitting attackers to supply file:// scheme URLs that bypass validation and are passed directly to git clone, enabling unauthorized access to all tracked file contents on the server filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59703.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59703
- https://www.vulncheck.com/advisories/repomix-local-file-inclusion-via-file-url-scheme-in-git-clone-endpoint
- https://github.com/yamadashy/repomix/issues/1704
- https://github.com/CrazyForks/repomix/commit/c748b524f41225e7fc6f89ad0084520901a453cf
- https://github.com/yamadashy/repomix
