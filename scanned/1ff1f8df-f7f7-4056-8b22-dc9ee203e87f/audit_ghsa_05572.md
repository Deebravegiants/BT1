# [H] Bagisto has Normal & Blind SSTI from low-privilege user when ordering product

## Summary
Severity: High
Advisory: GHSA-5j4h-4f72-qpm6
CVE: CVE-2026-21448
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-5j4h-4f72-qpm6
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <2.3.10

## Details
### Summary
SSTI when normal customer orders any product in add address step can inject value run in admin view.
### Details
`As normal user`
1. Go to `http://127.0.0.1:8000/`
2. Add order to cart and continue to checkout 
3. In step of add address inject this value {{7*7}} in any input

`As admin`
1. Go to `http://127.0.0.1:8000/admin/sales/orders`
2. And notice the vlaue appear in admin view 49

`As normal user`
3. Go to add address normally `http://127.0.0.1:8000/customer/account/addresses/create` and inject {{7*7}} on it and will notice it appear 49
<img width="1868" height="868" alt="image" src="https://github.com/user-attachments/assets/279627e9-6361-4d39-a500-0fc20e163d25" />


### PoC
 - Video attached with the report:  https://github.com/user-attachments/assets/a814b30c-a3e2-4a40-8644-336e21e60d0d


### Impact
- Can lead to RCE

## References
- https://github.com/bagisto/bagisto/security/advisories/GHSA-5j4h-4f72-qpm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-21448
- https://github.com/bagisto/bagisto
- https://github.com/bagisto/bagisto/releases/tag/v2.3.10
