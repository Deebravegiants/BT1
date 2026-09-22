# [M] Filebeat Beats has Buffer Overflow via Malformed Syslog Message or Malicious Tokenizer Pattern in Dissect Configuration

## Summary
Severity: Medium
Advisory: GHSA-2mj3-6grc-px38
CVE: CVE-2025-68383
CWE: CWE-120, CWE-1284
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-2mj3-6grc-px38
Type: github-advisory

## Affected
- Go: `github.com/elastic/beats/v7` — affected >=7.7.0 <8.19.9
- Go: `github.com/elastic/beats/v7` — affected >=9.0.0 <9.1.9
- Go: `github.com/elastic/beats/v7` — affected >=9.2.0 <9.2.3
- Go: `github.com/elastic/beats/v7` — affected >=0 <7.0.0-alpha2.0.20251204214633-dd3af18220bf
- Go: `github.com/elastic/beats` — affected >=0

## Details
Improper Validation of Specified Index, Position, or Offset in Input (CWE-1285) in Filebeat Syslog parser and the Libbeat Dissect processor can allow a user to trigger a Buffer Overflow (CAPEC-100) and cause a denial of service (panic/crash) of the Filebeat process via either a malformed Syslog message or a malicious tokenizer pattern in the Dissect configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68383
- https://github.com/elastic/beats/commit/27a168fb1c598d4a16748e9a7382bc0d197335a5
- https://github.com/elastic/beats/commit/2f971a057eea68e057b47829950cd8c26805df30
- https://github.com/elastic/beats/commit/339fa3f887a14c91e0c955b50a3b8819393bd632
- https://discuss.elastic.co/t/filebeat-8-19-9-9-1-9-and-9-2-3-security-update-esa-2025-32/384180
- https://github.com/elastic/elasticsearch
