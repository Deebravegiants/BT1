# [C] CVE-2021-30180

## Summary
Severity: Critical
Advisory: CVE-2021-30180
Aliases: GHSA-7wfc-x4f7-gg2x
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-30180
Type: osv

## Details
Apache Dubbo prior to 2.7.9 support Tag routing which will enable a customer to route the request to the right server. These rules are used by the customers when making a request in order to find the right endpoint. When parsing these YAML rules, Dubbo customers may enable calling arbitrary constructors.

## References
- https://lists.apache.org/thread.html/raed526465e56204030ddf374b1959478a290e7511971d7aba2e9e39b%40%3Cdev.dubbo.apache.org%3E
