# [M] repomix - Server-Side Request Forgery via Unvalidated Repository URLs in POST /api/pack

## Summary
Severity: Medium
Advisory: CVE-2026-59702
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59702
Type: osv

## Details
repomix contains a server-side request forgery vulnerability in the POST /api/pack endpoint that allows unauthenticated attackers to make arbitrary outbound requests. The endpoint fails to properly validate http://, https://, and file:// URLs before passing them to git clone, enabling attackers to access private network addresses, GCP metadata services, or local filesystem paths.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59702.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59702
- https://www.vulncheck.com/advisories/repomix-server-side-request-forgery-via-unvalidated-repository-urls-in-post-api-pack
- https://github.com/yamadashy/repomix/issues/1703
- https://github.com/CrazyForks/repomix/commit/c748b524f41225e7fc6f89ad0084520901a453cf
- https://github.com/yamadashy/repomix
