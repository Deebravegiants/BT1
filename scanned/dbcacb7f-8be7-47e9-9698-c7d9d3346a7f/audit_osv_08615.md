# [H] CVE-2016-4817

## Summary
Severity: High
Advisory: CVE-2016-4817
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-19
Source: https://osv.dev/vulnerability/CVE-2016-4817
Type: osv

## Details
lib/http2/connection.c in H2O before 1.7.3 and 2.x before 2.0.0-beta5 mishandles HTTP/2 disconnection, which allows remote attackers to cause a denial of service (use-after-free and application crash) or possibly execute arbitrary code via a crafted packet.

## References
- http://jvn.jp/en/jp/JVN87859762/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2016-000091
- https://github.com/h2o/h2o/pull/920
- https://github.com/h2o/h2o/commit/1c0808d580da09fdec5a9a74ff09e103ea058dd4
