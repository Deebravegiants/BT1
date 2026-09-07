# [H] directus vulnerable to HTML Injection in Password Reset email to custom Reset URL

## Summary
Severity: High
Advisory: GHSA-4hmq-ggrm-qfc6
CVE: CVE-2023-27474
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-4hmq-ggrm-qfc6
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <9.23.0

## Details
### Impact

Instances relying on an allow-listed reset URL are vulnerable to an HTML injection attack through the use of query parameters in the reset URL. 

### Patches

The problem has been resolved and released under version 9.23.0. People relying on a custom password reset URL should upgrade to 9.23.0 or later, or remove the custom reset url from the configured allow list.

### Workarounds

Disable the custom reset URL allow list.

## References
- https://github.com/directus/directus/security/advisories/GHSA-4hmq-ggrm-qfc6
- https://nvd.nist.gov/vuln/detail/CVE-2023-27474
- https://github.com/directus/directus/issues/17119
- https://github.com/directus/directus/pull/17120
- https://github.com/directus/directus
