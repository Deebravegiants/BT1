# [M] Metricbeat affected by multiple denial of service vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-w2gr-585j-r428
CVE: CVE-2026-0528
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-w2gr-585j-r428
Type: github-advisory

## Affected
- Go: `github.com/elastic/beats/v7` — affected >=0 <7.0.0-alpha2.0.20251217054608-6e42552a23ce
- Go: `github.com/elastic/beats/v7` — affected >=8.0.0 <8.19.10
- Go: `github.com/elastic/beats/v7` — affected >=9.0.0 <9.1.10
- Go: `github.com/elastic/beats/v7` — affected >=9.2.0 <9.2.4

## Details
Improper Validation of Array Index (CWE-129) exists in Metricbeat can allow an attacker to cause a Denial of Service through Input Data Manipulation (CAPEC-153) via specially crafted, malformed payloads sent to the Graphite server metricset or Zookeeper server metricset. Additionally, Improper Input Validation (CWE-20) exists in the Prometheus helper module that can allow an attacker to cause a Denial of Service through Input Data Manipulation (CAPEC-153) via specially crafted, malformed metric data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0528
- https://github.com/elastic/beats/commit/0025fbfe668936eb8fa65b838508faf3c3c04387
- https://github.com/elastic/beats/commit/6e42552a23cec734e7977ebd3eb7fb797ddce456
- https://github.com/elastic/beats/commit/c7664c91a5a68c2df782bfeffe4fb7f42ff2ad1a
- https://discuss.elastic.co/t/metricbeat-8-19-10-9-1-10-9-2-4-security-update-esa-2026-01/384519
- https://github.com/elastic/beats
