# [H] Vvveb: Vvveb CMS — Negative-quantity cart manipulation allows creation of orders with negative grand totals

## Summary
Severity: High
Advisory: CVE-2026-44826
Aliases: GHSA-75x2-j47j-mg8j
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-44826
Type: osv

## Details
Vvveb is a powerful and easy to use CMS with page builder to build websites, blogs or ecommerce stores. Prior to 1.0.8.2, Vvveb CMS does not validate the sign of the quantity parameter on the cart-add endpoint. Submitting a negative integer is accepted by the server and treated as a normal positive line-item, but with the sign carried through into every downstream computation: line total, sub-total, taxes, and grand total all become negative numbers. The customer-facing cart UI then displays a negative grand total to the user, the checkout flow accepts the negative cart, and the resulting order is persisted in the merchant's database with a negative total column. From the merchant's order management dashboard, this surfaces as a real order with a negative total — an "the merchant owes the customer money" record that no legitimate workflow ever creates. This vulnerability is fixed in 1.0.8.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44826.json
- https://github.com/givanz/Vvveb/security/advisories/GHSA-75x2-j47j-mg8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-44826
