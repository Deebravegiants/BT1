# [H] HTTPX2: Streaming response decompression does not bound peak memory (decompression amplification)

## Summary
Severity: High
Advisory: CVE-2026-84382
Aliases: GHSA-8xx6-hgc6-gc2m, PYSEC-2026-3846
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84382
Type: osv

## Details
HTTPX2 is a next generation HTTP client for Python. Prior to 2.12.0, the HTTPX2 content decoders in src/httpx2/httpx2/_decoders.py fully inflate each gzip, deflate, br, or zstd network chunk before iter_bytes() or aiter_bytes() yields bounded pieces to the application. A 64 KiB compressed chunk can expand to approximately 64 MiB in one intermediate allocation, so an attacker-controlled or compromised server can cause severe memory pressure or out-of-memory process termination even when the application streams the response. This issue is fixed in version 2.12.0.

## References
- https://github.com/pydantic/httpx2/releases/tag/v2.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84382.json
- https://github.com/pydantic/httpx2/security/advisories/GHSA-8xx6-hgc6-gc2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-84382
- https://github.com/pydantic/httpx2/commit/4fd0c70a3f207c618b145934792f791bccfb39f8
- https://github.com/pydantic/httpx2/pull/1126
