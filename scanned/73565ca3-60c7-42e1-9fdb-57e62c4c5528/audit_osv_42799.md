# [C] unstructured: Server-Side Request Forgery in the URL-based partitioning

## Summary
Severity: Critical
Advisory: CVE-2026-71428
Aliases: GHSA-4mvj-m6j5-pmf7, PYSEC-2026-3930
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-71428
Type: osv

## Details
The unstructured library provides open-source components for ingesting and pre-processing images and text documents, such as PDFs, HTML, Word docs, and many more. From 0.4.7 until 0.24.0, the url argument of partition, partition_html, and partition_md is fetched without host validation in unstructured/partition/auto.py, unstructured/partition/html/partition.py, and unstructured/partition/md.py. An attacker who controls that URL can make a server-side ingestion service request loopback addresses, internal HTTP services, or cloud metadata endpoints through direct targets, redirects, or DNS rebinding. The response body is returned as Element text, allowing internal response disclosure, and side-effecting GET endpoints may also be triggered. This issue is fixed in version 0.24.0.

## References
- https://github.com/Unstructured-IO/unstructured/releases/tag/0.24.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71428.json
- https://github.com/Unstructured-IO/unstructured/security/advisories/GHSA-4mvj-m6j5-pmf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-71428
- https://github.com/Unstructured-IO/unstructured/commit/445c95735c4045057f51f399bc04c657751923bd
- https://github.com/Unstructured-IO/unstructured/pull/4388
