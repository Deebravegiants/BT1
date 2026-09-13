# [C] Use of a Broken or Risky Cryptographic Algorithm in Apache Hadoop

## Summary
Severity: Critical
Advisory: GHSA-q46v-cj5v-hvg6
CVE: CVE-2012-4449
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q46v-cj5v-hvg6
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-client` — affected >=0 <0.23.4
- Maven: `org.apache.hadoop:hadoop-client` — affected >=1.0.0 <1.0.4
- Maven: `org.apache.hadoop:hadoop-client` — affected >=2.0.0 <2.0.2

## Details
Apache Hadoop before 0.23.4, 1.x before 1.0.4, and 2.x before 2.0.2 generate token passwords using a 20-bit secret when Kerberos security features are enabled, which makes it easier for context-dependent attackers to crack secret keys via a brute-force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4449
- https://www.cloudera.com/documentation/other/security-bulletins/topics/csb_topic_1.html#topic_1_0
- http://mail-archives.apache.org/mod_mbox/hadoop-general/201210.mbox/%3CCA+z3+9FYdPmzBEaMZ71SUqzRx=eU=o4mSHUsbrpzgR9X_F1c0Q@mail.gmail.com%3E
