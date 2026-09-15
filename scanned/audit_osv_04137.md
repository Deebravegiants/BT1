# [M] BIT-apisix-2020-13945

## Summary
Severity: Medium
Advisory: BIT-apisix-2020-13945
Aliases: CVE-2020-13945
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apisix-2020-13945
Type: osv

## Affected
- Bitnami: `apisix` — affected >=1.2.0 <1.5.1

## Details
In Apache APISIX, the user enabled the Admin API and deleted the Admin API access IP restriction rules. Eventually, the default token is allowed to access APISIX management data. This affects versions 1.2, 1.3, 1.4, 1.5.

## References
- http://packetstormsecurity.com/files/166228/Apache-APISIX-Remote-Code-Execution.html
- https://lists.apache.org/thread.html/r792feb29964067a4108f53e8579a1e9bd1c8b5b9bc95618c814faf2f%40%3Cdev.apisix.apache.org%3E
- https://nvd.nist.gov/vuln/detail/CVE-2020-13945
