# [M] Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-4r8q-gv9j-3xx6
CVE: CVE-2021-32645
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-4r8q-gv9j-3xx6
Type: github-advisory

## Affected
- Packagist: `hyn/multi-tenant` — affected >=5.6.0 <5.7.2

## Details
### Impact
In some situations, it is possible to have open redirects where users can be redirected from your site to any other site using a specially crafted URL.
This is only the case for installations where the default Hostname Identification is used and the environment uses tenants that have `force_https` set to `true` (default: `false`)

### Patches
Version 5.7.2 contains the relevant patches to fix this bug. Stripping the URL from special characters to prevent specially crafted URL's from being redirected to.

### Workarounds
There is a simple way to work around the security issue
- Set the `force_https` to every tenant to `false`

### References
https://nvd.nist.gov/vuln/detail/CVE-2018-11784

### For more information
If you have any questions or comments about this advisory:
* Contact us in Discord: https://tenancy.dev/chat

## References
- https://github.com/tenancy/multi-tenant/security/advisories/GHSA-4r8q-gv9j-3xx6
- https://nvd.nist.gov/vuln/detail/CVE-2021-32645
- https://github.com/tenancy/multi-tenant/commit/9c837a21bccce9bcaeb90033ef200d84f0d9e164
- https://packagist.org/packages/hyn/multi-tenant
- https://webmasters.googleblog.com/2009/01/open-redirect-urls-is-your-site-being.html
