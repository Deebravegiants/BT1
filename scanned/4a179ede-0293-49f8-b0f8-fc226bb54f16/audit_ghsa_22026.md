# [H] Improper Access Control in Elasticsearch

## Summary
Severity: High
Advisory: GHSA-fh5x-4j57-6q5x
CVE: CVE-2015-4165
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-fh5x-4j57-6q5x
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=0 <1.6.0

## Details
The snapshot API in Elasticsearch before 1.6.0 when another application exists on the system that can read Lucene files and execute code from them, is accessible by the attacker, and the Java VM on which Elasticsearch is running can write to a location that the other application can read and execute from, allows remote authenticated users to write to and create arbitrary snapshot metadata files, and potentially execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-4165
- https://bugzilla.redhat.com/show_bug.cgi?id=1230761
- https://www.elastic.co/community/security
- http://packetstormsecurity.com/files/132234/Elasticsearch-1.5.2-File-Creation.html
