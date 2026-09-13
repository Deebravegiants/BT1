# [H] Apache Solr: Solr Schema Designer blindly "trusts" all configsets, possibly leading to RCE by unauthenticated users

## Summary
Severity: High
Advisory: BIT-solr-2023-50292
Aliases: CVE-2023-50292, GHSA-4wxw-42wx-2wfx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-solr-2023-50292
Type: osv

## Affected
- Bitnami: `solr` — affected >=9.0.0 <9.4.1

## Details
Incorrect Permission Assignment for Critical Resource, Improper Control of Dynamically-Managed Code Resources vulnerability in Apache Solr.

This issue affects Apache Solr: from 8.10.0 through 8.11.2, from 9.0.0 before 9.3.0.

The Schema Designer was introduced to allow users to more easily configure and test new Schemas and configSets.
However, when the feature was created, the "trust" (authentication) of these configSets was not considered.
External library loading is only available to configSets that are "trusted" (created by authenticated users), thus non-authenticated users are unable to perform Remote Code Execution.
Since the Schema Designer loaded configSets without taking their "trust" into account, configSets that were created by unauthenticated users were allowed to load external libraries when used in the Schema Designer.

Users are recommended to upgrade to version 9.3.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/02/09/3
- https://solr.apache.org/security.html#cve-2023-50298-apache-solr-can-expose-zookeeper-credentials-via-streaming-expressions
- https://nvd.nist.gov/vuln/detail/CVE-2023-50292
