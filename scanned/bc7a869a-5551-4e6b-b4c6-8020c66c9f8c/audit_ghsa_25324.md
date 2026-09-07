# [M] Use of Password Hash With Insufficient Computational Effort in Apache Derby

## Summary
Severity: Medium
Advisory: GHSA-fh32-35w2-rxcc
CVE: CVE-2009-4269
CWE: CWE-916
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-fh32-35w2-rxcc
Type: github-advisory

## Affected
- Maven: `org.apache.derby:derby` — affected >=0 <10.6.1.0

## Details
The password hash generation algorithm in the BUILTIN authentication functionality for Apache Derby before 10.6.1.0 performs a transformation that reduces the size of the set of inputs to SHA-1, which produces a small search space that makes it easier for local and possibly remote attackers to crack passwords by generating hash collisions, related to password substitution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-4269
- https://github.com/apache/derby/commit/178ca0cfb796b5a5788d25ded0978773ea254332
- https://github.com/apache/derby/commit/23f97a597716ee5b08eff698b7177850ad8e1294
- https://github.com/apache/derby/commit/3b82686e32a8d4fa2027350279104f9b243b35d6
- https://github.com/apache/derby/commit/60edeb0cb29daf9d28ece1863db779c1af5a3f62
- https://github.com/apache/derby/commit/8c305e2f3fad1c3a4f98c06c7f2b53e2bfdd308c
- https://issues.apache.org/jira/browse/DERBY-4483
- http://db.apache.org/derby/releases/release-10.6.1.0.cgi#Fix+for+Security+Bug+CVE-2009-4269
- http://marc.info/?l=apache-db-general&m=127428514905504&w=1
- http://www.oracle.com/technetwork/topics/security/cpujan2011-194091.html
