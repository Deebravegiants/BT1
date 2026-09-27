# [C] CVE-2016-4303

## Summary
Severity: Critical
Advisory: CVE-2016-4303
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-4303
Type: osv

## Details
The parse_string function in cjson.c in the cJSON library mishandles UTF8/16 strings, which allows remote attackers to cause a denial of service (crash) or execute arbitrary code via a non-hex character in a JSON string, which triggers a heap-based buffer overflow.

## References
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00082.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00090.html
- http://software.es.net/iperf/news.html#security-issue-iperf-3-1-3-iperf-3-0-12-released
- https://lists.debian.org/debian-lts-announce/2020/01/msg00023.html
- https://raw.githubusercontent.com/esnet/security/master/cve-2016-4303/esnet-secadv-2016-0001.txt.asc
- https://github.com/esnet/iperf/commit/91f2fa59e8ed80dfbf400add0164ee0e508e412a
- http://blog.talosintel.com/2016/06/esnet-vulnerability.html
- http://www.talosintelligence.com/reports/TALOS-2016-0164/
