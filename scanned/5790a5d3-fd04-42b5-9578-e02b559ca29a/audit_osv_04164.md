# [M] Bypass network access control

## Summary
Severity: Medium
Advisory: BIT-apisix_dashboard-2021-33190
Aliases: CVE-2021-33190
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apisix_dashboard-2021-33190
Type: osv

## Affected
- Bitnami: `apisix_dashboard` — affected >=2.6.0 <2.6.1

## Details
In Apache APISIX Dashboard version 2.6, we changed the default value of listen host to 0.0.0.0 in order to facilitate users to configure external network access. In the IP allowed list restriction, a risky function was used for the IP acquisition, which made it possible to bypass the network limit. At the same time, the default account and password are fixed.Ultimately these factors lead to the issue of security risks. This issue is fixed in APISIX Dashboard 2.6.1

## References
- http://www.openwall.com/lists/oss-security/2021/06/08/4
- https://lists.apache.org/thread.html/re736aea55e8fd2478f0739c0c38a9375c4204fc1f0bd1ea687f57049%40%3Cdev.apisix.apache.org%3E
- https://nvd.nist.gov/vuln/detail/CVE-2021-33190
