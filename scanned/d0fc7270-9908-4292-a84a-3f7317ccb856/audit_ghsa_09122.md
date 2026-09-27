# [H] Nautobot: Webhook definitions could be used for server-side request forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-c35q-vxrp-ph26
CVE: CVE-2026-44797
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-c35q-vxrp-ph26
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=3.0.0a2 <3.1.2
- PyPI: `nautobot` — affected >=0 <2.4.33

## Details
### Impact

Nautobot's `Webhook` data model and associated feature set could be configured by users with sufficient access to perform requests to various hosts and IP addresses that should not be permitted, allowing for various behaviors similar to server-side request forgery (SSRF).

### Patches

Fixes are available in Nautobot v2.4.33 and v3.1.2.

In support of this fix, three new settings variables have been added to Nautobot:

- `WEBHOOK_ALLOWED_SCHEMES` - By default new or updated `Webhook` records will be restricted to HTTP or HTTPS only, disallowing other schemes that may have been previously allowed. Administrators should audit existing `Webhook` records to identify any that are invalid, and either update/delete said records or customize `WEBHOOK_ALLOWED_SCHEMES` as appropriate.
- `WEBHOOK_ADDITIONAL_BLOCKED_NETWORKS` - This can be used to specify additional IP networks that should be denied to `Webhook` sending, for example some deployments may wish to disallow RFC1918 addresses or even disallow all networks and carve out specific exemptions using the following setting.
- `WEBHOOK_ALLOWED_HOSTS` - This can be used to provide an allow-list of specific hosts that would otherwise be blocked by any `WEBHOOK_ADDITIONAL_BLOCKED_NETWORKS` configuration.

### Workarounds

Administrators should review which users have been granted `add` or `change` permissions for the `Webhook` data model, and should review currently defined `Webhook` records for safety and validity. Other than that, no specific workaround has been identified.

### References

- 2.4.33 (<a href="https://github.com/nautobot/nautobot/commit/16aa4aa9796ab7a31c4d615ec945e1f16d8c77c4">patch</a>)
- 3.1.2 (<a href="https://github.com/nautobot/nautobot/commit/7324c8f0d8c7245fbc691e15d729adc2d2707d08">patch</a>)

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-c35q-vxrp-ph26
- https://nvd.nist.gov/vuln/detail/CVE-2026-44797
- https://github.com/nautobot/nautobot/commit/16aa4aa9796ab7a31c4d615ec945e1f16d8c77c4
- https://github.com/nautobot/nautobot/commit/7324c8f0d8c7245fbc691e15d729adc2d2707d08
- https://github.com/nautobot/nautobot
- https://github.com/nautobot/nautobot/releases/tag/v2.4.33
- https://github.com/nautobot/nautobot/releases/tag/v3.1.2
