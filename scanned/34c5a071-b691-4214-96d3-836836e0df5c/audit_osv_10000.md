# [M] CVE-2017-12625

## Summary
Severity: Medium
Advisory: CVE-2017-12625
Aliases: GHSA-2g9q-chq2-w8qw
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-12625
Type: osv

## Details
Apache Hive 2.1.x before 2.1.2, 2.2.x before 2.2.1, and 2.3.x before 2.3.1 expose an interface through which masking policies can be defined on tables or views, e.g., using Apache Ranger. When a view is created over a given table, the policy enforcement does not happen correctly on the table for masked columns.

## References
- http://mail-archives.apache.org/mod_mbox/hive-user/201710.mbox/%3C3791103E-80D5-4E75-AF23-6F8ED54DDEBE%40apache.org%3E
- http://www.securityfocus.com/bid/101686
