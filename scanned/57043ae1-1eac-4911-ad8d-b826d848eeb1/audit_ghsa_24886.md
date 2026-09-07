# [H] Cezerin Unauthorized Acces

## Summary
Severity: High
Advisory: GHSA-6pq6-crw9-522h
CVE: CVE-2019-18608
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6pq6-crw9-522h
Type: github-advisory

## Affected
- npm: `cezerin` — affected >=0

## Details
Cezerin v0.33.0 allows unauthorized order-information modification because certain internal attributes can be overwritten via a conflicting name when processing order requests. Hence, a malicious customer can manipulate an order (e.g., its payment status or shipping fee) by adding additional attributes to user-input during the PUT `/ajax/cart` operation for a checkout, because of `getValidDocumentForUpdate` in `api/server/services/orders/orders.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18608
- https://github.com/cezerin/cezerin
- https://github.com/cl0udz/vulnerabilities/blob/master/cezerin-manipulate_order_information/README.md
