# [M] Leantime Server-Side Request Forgery and Local File Inclusion in Blueprints::import()

## Summary
Severity: Medium
Advisory: CVE-2026-66415
Aliases: GHSA-gphg-6h4g-mg22
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-66415
Type: osv

## Details
Leantime 3.6.2 contains a server-side request forgery and local file inclusion vulnerability that allows authenticated attackers to read internal resources by passing unsanitized user-supplied filenames to file_get_contents() in the Blueprints::import() method without path validation. Attackers can submit crafted filenames containing URL wrappers or path traversal sequences through the JSON-RPC API endpoint to access cloud metadata services or read arbitrary files from the server filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66415.json
- https://github.com/javokhir-sec/CVE-PoC-Hub/security/advisories/GHSA-gphg-6h4g-mg22
- https://nvd.nist.gov/vuln/detail/CVE-2026-66415
- https://www.vulncheck.com/advisories/leantime-server-side-request-forgery-and-local-file-inclusion-in-blueprints-import
- https://github.com/Leantime/leantime/pull/3656
- https://github.com/Leantime/leantime
