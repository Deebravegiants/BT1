# [C] OrientDB vulnerable to Improper Privilage Management leading to arbitrary command injection

## Summary
Severity: Critical
Advisory: GHSA-xm6r-4466-mr74
CVE: CVE-2017-11467
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-xm6r-4466-mr74
Type: github-advisory

## Affected
- Maven: `com.orientechnologies:orientdb-core` — affected >=0 <2.2.23

## Details
OrientDB through 2.2.22 does not enforce privilege requirements during "where" or "fetchplan" or "order by" use, which allows remote attackers to execute arbitrary OS commands via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11467
- https://github.com/advisories/GHSA-xm6r-4466-mr74
- https://github.com/orientechnologies/orientdb
- https://github.com/orientechnologies/orientdb/wiki/OrientDB-2.2-Release-Notes#2223---july-11-2017
- https://web.archive.org/web/20210403135751/http://www.heavensec.org/?p=1703
