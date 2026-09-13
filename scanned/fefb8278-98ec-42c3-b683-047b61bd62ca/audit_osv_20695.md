# [H] CVE-2021-36162

## Summary
Severity: High
Advisory: CVE-2021-36162
Aliases: GHSA-r577-4hq7-73qh
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-36162
Type: osv

## Details
Apache Dubbo supports various rules to support configuration override or traffic routing (called routing in Dubbo). These rules are loaded into the configuration center (eg: Zookeeper, Nacos, ...) and retrieved by the customers when making a request in order to find the right endpoint. When parsing these YAML rules, Dubbo customers will use SnakeYAML library to load the rules which by default will enable calling arbitrary constructors. An attacker with access to the configuration center he will be able to poison the rule so when retrieved by the consumers, it will get RCE on all of them. This was fixed in Dubbo 2.7.13, 3.0.2

## References
- https://lists.apache.org/thread.html/rfa351115a459e214b99ffcc52c35f33359f3370c547d9c6ba1a60037%40%3Cdev.dubbo.apache.org%3E
