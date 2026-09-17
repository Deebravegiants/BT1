# [C] security vulnerability on unauthorized access.

## Summary
Severity: Critical
Advisory: BIT-apisix_dashboard-2021-45232
Aliases: CVE-2021-45232
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apisix_dashboard-2021-45232
Type: osv

## Affected
- Bitnami: `apisix_dashboard` — affected >=0 <2.10.1

## Details
In Apache APISIX Dashboard before 2.10.1, the Manager API uses two frameworks and introduces framework `droplet` on the basis of framework `gin`, all APIs and authentication middleware are developed based on framework `droplet`, but some API directly use the interface of framework `gin` thus bypassing the authentication.

## References
- http://www.openwall.com/lists/oss-security/2021/12/27/1
- https://lists.apache.org/thread/979qbl6vlm8269fopfyygnxofgqyn6k5
- https://nvd.nist.gov/vuln/detail/CVE-2021-45232
