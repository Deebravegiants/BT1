# [M] HTTPX2: Conflicting Content-Length and Transfer-Encoding headers can be auto-generated

## Summary
Severity: Medium
Advisory: CVE-2026-84380
Aliases: GHSA-pf96-p4fj-6566, PYSEC-2026-3849
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84380
Type: osv

## Details
HTTPX2 is a next generation HTTP client for Python. Prior to 2.11.0, Request._prepare() in src/httpx2/httpx2/_models.py can add a body-derived Content-Length header to a request that already contains a caller-supplied Transfer-Encoding header because its setdefault() processing checks each default header independently rather than treating the two framing headers as mutually exclusive. Fixed-size byte, JSON, form, and known-length multipart bodies can therefore be serialized over HTTP/1.1 with both headers, allowing request smuggling or connection desynchronization when downstream intermediaries disagree about which framing header takes precedence. This issue is fixed in version 2.11.0.

## References
- https://github.com/pydantic/httpx2/releases/tag/v2.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84380.json
- https://github.com/pydantic/httpx2/security/advisories/GHSA-pf96-p4fj-6566
- https://nvd.nist.gov/vuln/detail/CVE-2026-84380
- https://github.com/pydantic/httpx2/commit/829b93a2393212996f613e635261f777d9ec6eab
- https://github.com/pydantic/httpx2/pull/1137
