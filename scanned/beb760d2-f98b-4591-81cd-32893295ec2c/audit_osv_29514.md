# [H] Apache Lucene.Net.Replicator: Remote Code Execution in Lucene.Net.Replicator

## Summary
Severity: High
Advisory: CVE-2024-43383
Aliases: GHSA-2qw8-ppr5-m96c
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-31
Source: https://osv.dev/vulnerability/CVE-2024-43383
Type: osv

## Details
Deserialization of Untrusted Data vulnerability in Apache Lucene.Net.Replicator.

This issue affects Apache Lucene.NET's Replicator library: from 4.8.0-beta00005 through 4.8.0-beta00016.

An attacker that can intercept traffic between a replication client and server, or control the target replication node URL, can provide a specially-crafted JSON response that is deserialized as an attacker-provided exception type. This can result in remote code execution or other potential unauthorized access.


Users are recommended to upgrade to version 4.8.0-beta00017, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/10/31/2
- https://www.nuget.org/packages/Lucene.Net.Replicator/4.8.0-beta00016
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43383.json
- https://lists.apache.org/thread/wlz1p76dxpt4rl9o29voxjd5zl7717nh
- https://nvd.nist.gov/vuln/detail/CVE-2024-43383
