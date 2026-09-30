# [C] CVE-2020-1947

## Summary
Severity: Critical
Advisory: CVE-2020-1947
Aliases: GHSA-v54f-xcmp-43cr
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-11
Source: https://osv.dev/vulnerability/CVE-2020-1947
Type: osv

## Details
In Apache ShardingSphere(incubator) 4.0.0-RC3 and 4.0.0, the ShardingSphere's web console uses the SnakeYAML library for parsing YAML inputs to load datasource configuration. SnakeYAML allows to unmarshal data to a Java type By using the YAML tag. Unmarshalling untrusted data can lead to security flaws of RCE.

## References
- https://lists.apache.org/thread.html/r4a61a24c119bd820da6fb02100d286f8aae55c8f9b94a346b9bb27d8%40%3Cdev.shardingsphere.apache.org%3E
