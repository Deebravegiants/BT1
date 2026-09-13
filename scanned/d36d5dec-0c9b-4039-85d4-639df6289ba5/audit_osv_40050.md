# [M] Banana Slides 0.4.0 Path Traversal via generate_image() in ai_service.py

## Summary
Severity: Medium
Advisory: CVE-2026-49136
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-49136
Type: osv

## Details
Banana Slides through 0.4.0, patched in commit e8bc490, contains a path traversal vulnerability in the generate_image() function within the AI service backend that allows unauthenticated attackers to read arbitrary image-format files outside the intended uploads directory by exploiting an incomplete path prefix check using os.path.startswith() without a trailing separator. Attackers can supply crafted markdown image references in user-controlled page descriptions that resolve to sibling directories whose names share the uploads folder prefix, bypassing the directory confinement check and causing the application to read files from unintended locations via PIL Image.open().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-49136
- https://www.vulncheck.com/advisories/banana-slides-path-traversal-via-generate-image-in-ai-service-py
- https://github.com/Anionex/banana-slides/issues/429
- https://github.com/Anionex/banana-slides/pull/430
- https://github.com/Anionex/banana-slides/commit/e8bc490ec8b4b657e07dc3ab4e94fbedcaade421
- https://github.com/Anionex/banana-slides
