# [H] Elasticsearch Logstash allows remote attackers to execute arbitrary commands

## Summary
Severity: High
Advisory: GHSA-8qhq-rq4j-8prj
CVE: CVE-2014-4326
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8qhq-rq4j-8prj
Type: github-advisory

## Affected
- RubyGems: `logstash` — affected >=1.0.14 <1.4.2

## Details
Elasticsearch Logstash 1.0.14 through 1.4.x before 1.4.2 allows remote attackers to execute arbitrary commands via a crafted event in (1) `zabbix.rb` or (2) `nagios_nsca.rb` in `outputs/`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4326
- https://github.com/elastic/logstash
- https://web.archive.org/web/20140804031140/http://www.elasticsearch.org/blog/logstash-1-4-2
- https://web.archive.org/web/20201207013408/http://www.securityfocus.com/archive/1/532841/100/0/threaded
- https://www.elastic.co/community/security
