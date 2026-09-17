# [H] CVE-2026-9563

## Summary
Severity: High
Advisory: CVE-2026-9563
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-9563
Type: osv

## Details
In Eclipse Parsson published Maven Central artifacts before version 1.1.8, the JSON parser did not enforce a default maximum on the number of characters consumed while parsing a single JSON document. Applications that parse attacker- controlled JSON can be forced to consume excessive CPU and memory by processing very large documents, including large arrays, objects, strings, numbers, whitespace, or nested structures, resulting in a denial of service. Eclipse Parsson 1.1.8 introduces a configurable maximum parsing limit with a default limit of 15 million parser-consumed characters.

## References
- https://github.com/eclipse-ee4j/parsson/tree/1.1.8
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/444
- https://repo.maven.apache.org/maven2/org/eclipse/parsson/parsson/1.1.8/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9563.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9563
- https://github.com/eclipse-ee4j/parsson/commit/134e8d101aa74c8b9302d0cb62f6ccb4912a9d0c
- https://github.com/eclipse-ee4j/parsson/pull/169
