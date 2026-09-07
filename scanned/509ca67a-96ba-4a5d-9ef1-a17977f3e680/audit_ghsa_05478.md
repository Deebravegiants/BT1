# [H] Devalue is vulnerable to denial of service due to memory exhaustion in devalue.parse

## Summary
Severity: High
Advisory: GHSA-vw5p-8cq8-m7mv
CVE: CVE-2026-22774
CWE: CWE-20, CWE-405
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-vw5p-8cq8-m7mv
Type: github-advisory

## Affected
- npm: `devalue` — affected >=5.3.0 <5.6.2

## Details
## Summary

Certain inputs can cause `devalue.parse` to consume excessive CPU time and/or memory, potentially leading to denial of service in systems that parse input from untrusted sources. This affects applications using `devalue.parse` on externally-supplied data. The root cause is the typed array hydration expecting an `ArrayBuffer` as input, but not checking the assumption before creating the typed array.

## Details

The parser's typed array hydration logic does not properly validate input before processing. Specially crafted inputs can cause disproportionate memory allocation or CPU usage on the receiving system.

## Impact

This is a denial of service vulnerability affecting systems that use `devalue.parse` to handle data from potentially untrusted sources.

Affected systems should upgrade to patched versions immediately.

## References
- https://github.com/sveltejs/devalue/security/advisories/GHSA-vw5p-8cq8-m7mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-22774
- https://github.com/sveltejs/devalue/commit/11755849fa0634ae294a15ec0aef2f43efcad7c4
- https://github.com/sveltejs/devalue/commit/e46afa64dd2b25aa35fb905ba5d20cea63aabbf7
- https://github.com/sveltejs/devalue
- https://github.com/sveltejs/devalue/releases/tag/v5.6.2
