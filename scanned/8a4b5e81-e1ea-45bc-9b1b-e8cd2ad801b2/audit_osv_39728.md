# [M] Agent Zero < 1.15 Path Traversal File Read via image_get API

## Summary
Severity: Medium
Advisory: CVE-2026-47118
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-47118
Type: osv

## Details
Agent Zero before version 1.15 contains a path traversal vulnerability that allows unauthenticated attackers to read arbitrary files by supplying crafted paths to the image file serving endpoint, which relies solely on an extension allowlist while the path containment check is explicitly disabled. Attackers can request any file with an image extension readable by the process, including files outside the agent workspace, user home directories, and mounted volumes, and can also leverage symlink-based escapes due to the lack of path canonicalization in the path resolution logic.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47118.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47118
- https://www.vulncheck.com/advisories/agent-zero-path-traversal-file-read-via-image-get-api
- https://github.com/agent0ai/agent-zero/issues/1609
- https://github.com/3clyp50/agent-zero/commit/1f2d5122265282d6b98bc36ee8f9d0f8ab76db9e
- https://github.com/3clyp50/agent-zero
