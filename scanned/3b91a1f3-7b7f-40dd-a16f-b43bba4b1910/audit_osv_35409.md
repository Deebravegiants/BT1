# [M] MuPDF < 1.27.0-rc1 Stack Exhaustion DoS via EPUB CSS Rendering

## Summary
Severity: Medium
Advisory: CVE-2025-71382
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2025-71382
Type: osv

## Details
MuPDF before 1.27.0-rc1 contains an uncontrolled recursion vulnerability in the EPUB CSS rendering engine that allows remote attackers to cause a denial of service by supplying a maliciously crafted EPUB file with deeply nested HTML elements and inline CSS styles. The function value_from_inheritable_property() in css-apply.c recurses through the CSS property inheritance chain without a depth limit, exhausting the process stack and causing a crash in any application using MuPDF for EPUB rendering.

## References
- https://github.com/ArtifexSoftware/mupdf/releases/tag/1.27.0-rc1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71382.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71382
- https://www.vulncheck.com/advisories/mupdf-rc1-stack-exhaustion-dos-via-epub-css-rendering
- https://github.com/ArtifexSoftware/mupdf/commit/70b71ab22e6de4d4c44cd301c88231f623a4e94e
- https://github.com/ArtifexSoftware/mupdf
- https://bugs.ghostscript.com/show_bug.cgi?id=708840
