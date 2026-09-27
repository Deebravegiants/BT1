# [M] Cheshire Cat AI Memory Collection Endpoint Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-85093
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85093
Type: osv

## Details
Cheshire Cat AI's GET /memory/collections/{collection_id}/points endpoint fails to apply per-user filtering when retrieving episodic memory points. Authenticated attackers with MEMORY:READ permission can retrieve all users' stored conversation messages and personal data by paginating through the collection using the offset cursor.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85093.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85093
- https://www.vulncheck.com/advisories/cheshire-cat-ai-memory-collection-endpoint-information-disclosure
- https://github.com/cheshire-cat-ai/core/issues/1136
- https://github.com/cheshire-cat-ai/core
- https://github.com/cheshire-cat-ai/core/blob/1.9.2/core/cat/looking_glass/stray_cat.py
- https://github.com/cheshire-cat-ai/core/blob/1.9.2/core/cat/routes/memory/points.py#L350
