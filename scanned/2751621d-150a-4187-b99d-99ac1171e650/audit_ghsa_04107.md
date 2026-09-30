# [H] Improper Authorization in org.apache.hbase:hbase

## Summary
Severity: High
Advisory: GHSA-535v-4x9q-446c
CVE: CVE-2019-0212
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-02
Source: https://github.com/advisories/GHSA-535v-4x9q-446c
Type: github-advisory

## Affected
- Maven: `org.apache.hbase:hbase` — affected >=2.0.0 <2.0.5
- Maven: `org.apache.hbase:hbase` — affected >=2.1.0 <2.1.4

## Details
In all previously released Apache HBase 2.x versions (2.0.0-2.0.4, 2.1.0-2.1.3), authorization was incorrectly applied to users of the HBase REST server. Requests sent to the HBase REST server were executed with the permissions of the REST server itself, not with the permissions of the end-user. This issue is only relevant when HBase is configured with Kerberos authentication, HBase authorization is enabled, and the REST server is configured with SPNEGO authentication. This issue does not extend beyond the HBase REST server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0212
- https://github.com/advisories/GHSA-535v-4x9q-446c
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/66535e15007cda8f9308eec10e12ffe349e0b8b55e56ec6ee02b71d2@%3Cdev.hbase.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- http://www.openwall.com/lists/oss-security/2019/03/27/3
- http://www.securityfocus.com/bid/107624
