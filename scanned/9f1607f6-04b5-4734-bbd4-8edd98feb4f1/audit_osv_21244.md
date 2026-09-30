# [H] CVE-2021-41277

## Summary
Severity: High
Advisory: CVE-2021-41277
Aliases: GHSA-w73v-6p7p-fpfr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-11-17
Source: https://osv.dev/vulnerability/CVE-2021-41277
Type: osv

## Details
Metabase is an open source data analytics platform. In affected versions a security issue has been discovered with the custom GeoJSON map (`admin->settings->maps->custom maps->add a map`) support and potential local file inclusion (including environment variables). URLs were not validated prior to being loaded. This issue is fixed in a new maintenance release (0.40.5 and 1.40.5), and any subsequent release after that. If you’re unable to upgrade immediately, you can mitigate this by including rules in your reverse proxy or load balancer or WAF to provide a validation filter before the application.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-41277
- https://github.com/metabase/metabase/security/advisories/GHSA-w73v-6p7p-fpfr
- https://github.com/metabase/metabase/commit/042a36e49574c749f944e19cf80360fd3dc322f0
