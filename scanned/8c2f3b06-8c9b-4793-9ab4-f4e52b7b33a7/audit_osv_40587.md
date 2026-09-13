# [H] FOSSBilling's missing order-state validation allows clients to read and reset API key secrets for non-active orders

## Summary
Severity: High
Advisory: CVE-2026-53644
Aliases: GHSA-qf6j-vq68-qmfh
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-53644
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Versions 0.5.3 through 0.7.2 allow authenticated clients to both read and reset API key service secrets for orders that are no longer in an `active` state (e.g., `suspended`, `canceled`). The root cause is missing order-state validation in two client API endpoints, despite an `isActive()` helper already existing in the `Serviceapikey` module and the frontend UI correctly gating access on `order.status == 'active'`. Version 0.8.0 contains a fix. Some workarounds are available. If the `Serviceapikey` module is not needed, uninstall it to remove the affected endpoints. One may also use a reverse proxy or WAF to restrict access to `/api/client/order/service` and `/api/client/serviceapikey/reset` based on application-level order-state logic.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53644.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-qf6j-vq68-qmfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-53644
