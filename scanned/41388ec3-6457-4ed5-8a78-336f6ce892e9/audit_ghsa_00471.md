# [M] OrientDB Server Community Edition uses insufficiently random values to generate session IDs

## Summary
Severity: Medium
Advisory: GHSA-v6wr-fch2-vm5w
CVE: CVE-2015-2913
CWE: CWE-330
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-v6wr-fch2-vm5w
Type: github-advisory

## Affected
- Maven: `com.orientechnologies:orientdb-server` — affected >=0 <2.0.15
- Maven: `com.orientechnologies:orientdb-server` — affected >=2.1.0 <2.1.1

## Details
OrientDB Server Community Edition before 2.0.15 and 2.1.x before 2.1.1 improperly relies on the `java.util.Random` class for generation of random Session ID values in the `server/network/protocol/http/OHttpSessionManager.java`, which makes it easier for remote attackers to predict a value by determining the internal state of the PRNG in this class.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2913
- https://github.com/orientechnologies/orientdb/commit/668ece96be210e742a4e2820a3085b215cf55104
- https://github.com/advisories/GHSA-v6wr-fch2-vm5w
- https://github.com/orientechnologies/orientdb
- https://www.kb.cert.org/vuls/id/845332
