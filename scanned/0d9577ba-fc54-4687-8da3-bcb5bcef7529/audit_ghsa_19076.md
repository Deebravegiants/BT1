# [H] Instaclustr Cassandra-Lucene-Index allows bypass of Cassandra RBAC

## Summary
Severity: High
Advisory: GHSA-mrqp-q7vx-v2cx
CVE: CVE-2025-26511
CWE: CWE-288, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-13
Source: https://github.com/advisories/GHSA-mrqp-q7vx-v2cx
Type: github-advisory

## Affected
- Maven: `com.instaclustr:cassandra-lucene-index-plugin` — affected >=4.0-rc1-1.0.0 <4.0.17-1.0.0
- Maven: `com.instaclustr:cassandra-lucene-index-plugin` — affected >=4.1.0-1.0.0 <4.1.8-1.0.1

## Details
**Summary / Details**
Systems running the Instaclustr fork of Stratio's Cassandra-Lucene-Index plugin versions 4.0-rc1-1.0.0 through 4.0.16-1.0.0 and 4.1.0-1.0.0 through 4.1.8-1.0.0, installed into Apache Cassandra version 4.x, are susceptible to a vulnerability which when successfully exploited could allow authenticated Cassandra users to remotely bypass RBAC to access data and and escalate their privileges. 

**Affected Versions**
-	Cassandra-Lucene-Index plugin versions 4.0-rc1-1.0.0 through 4.0.16-1.0.0 
-	versions 4.1.0-1.0.0 through 4.1.8-1.0.0
when installed into Apache Cassandra version 4.x.

**Required Configuration for Exploit**
These are the conditions required to enable exploit:
1. Cassandra 4.x
2. Vulnerable version of the Cassandra-Lucene-Index plugin configured for use
3. Data added to tables
4. Lucene index created
5. Cassandra flush has run

**Mitigation/Prevention**
Mitigation requires dropping all Lucene indexes and stopping use of the plugin. Exploit will be possible any time the required conditions are met.

**Solution**
Upgrade to a fixed version of the Cassandra-Lucene-Index plugin.  
Review users in Cassandra to validate all superuser privileges.

## References
- https://github.com/instaclustr/cassandra-lucene-index/security/advisories/GHSA-mrqp-q7vx-v2cx
- https://nvd.nist.gov/vuln/detail/CVE-2025-26511
- https://github.com/instaclustr/cassandra-lucene-index/commit/44ab4b639c9354a6335f40b1cf6178c745c6e101
- https://github.com/instaclustr/cassandra-lucene-index/commit/94380b165bd3e597d3e22e47f8cc674ec7c7bf7f
- https://github.com/instaclustr/cassandra-lucene-index
