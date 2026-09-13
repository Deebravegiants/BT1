# [M] AnythingLLM: Windows path containment bypass in document folder route

## Summary
Severity: Medium
Advisory: CVE-2026-48789
Aliases: GHSA-j4m9-wwcq-m868
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48789
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. Prior to 1.13.0, on Windows, the document folder listing route can accept an encoded absolute Windows path that resolves outside the intended documents directory. The shared path containment helper rejects POSIX-style "../" traversal but does not reject Windows-style parent paths returned by path.relative(), such as "..". This vulnerability is fixed in 1.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48789.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-j4m9-wwcq-m868
- https://nvd.nist.gov/vuln/detail/CVE-2026-48789
