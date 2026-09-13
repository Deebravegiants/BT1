# [M] RediSearch Tag Injection in RedisChatMemoryRepository Allows Cross-Conversation Data Exposure

## Summary
Severity: Medium
Advisory: CVE-2026-59319
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59319
Type: osv

## Details
RedisChatMemoryRepository.findByMetadata() builds RediSearch tag and text queries from caller-supplied metadata values without applying RediSearchUtil.escape(), unlike get(), clear(), and findByTimeRange() in the same class which do escape their inputs. An application that passes user-controlled values to findByMetadata() on a tag-typed metadata field allows an attacker to inject RediSearch syntax (e.g. x} | *) that breaks out of the tag clause and matches all indexed chat messages across every conversation in the index.
Spring AI 2.0.0

## References
- https://spring.io/security/cve-2026-59319
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59319.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59319
