# [M] CVE-2018-11802

## Summary
Severity: Medium
Advisory: CVE-2018-11802
Aliases: GHSA-j346-h5wc-rw2m
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-04-01
Source: https://osv.dev/vulnerability/CVE-2018-11802
Type: osv

## Details
In Apache Solr, the cluster can be partitioned into multiple collections and only a subset of nodes actually host any given collection. However, if a node receives a request for a collection it does not host, it proxies the request to a relevant node and serves the request. Solr bypasses all authorization settings for such requests. This affects all Solr versions prior to 7.7 that use the default authorization mechanism of Solr (RuleBasedAuthorizationPlugin).

## References
- https://www.openwall.com/lists/oss-security/2019/04/24/1
