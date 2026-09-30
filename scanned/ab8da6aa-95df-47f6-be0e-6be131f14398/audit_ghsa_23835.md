# [H] Logstash Logs Sensitive Information

## Summary
Severity: High
Advisory: GHSA-vcmm-ppqx-95ch
CVE: CVE-2016-1000221
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vcmm-ppqx-95ch
Type: github-advisory

## Affected
- RubyGems: `logstash-core` — affected >=0 <2.3.4

## Details
Logstash prior to version 2.3.4, Elasticsearch Output plugin would log to file HTTP authorization headers which could contain sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000221
- https://github.com/elastic/logstash/commit/0999050144adad7f4d99d43e561c2882fd7c512b
- https://github.com/elastic/logstash
- https://web.archive.org/web/20210124065200/http://www.securityfocus.com/bid/99126
- https://www.elastic.co/community/security
