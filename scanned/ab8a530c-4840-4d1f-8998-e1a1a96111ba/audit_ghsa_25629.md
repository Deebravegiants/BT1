# [H] Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') in directus

## Summary
Severity: High
Advisory: GHSA-xmjj-3c76-5w84
CVE: CVE-2022-24814
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-05
Source: https://github.com/advisories/GHSA-xmjj-3c76-5w84
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <9.7.0

## Details
### Impact

Unauthorized JavaScript can be executed by inserting an iframe into the rich text html interface that links to a file uploaded HTML file that loads another uploaded JS file in its script tag. This satisfies the regular content security policy header, which in turn allows the file to run any arbitrary JS.

### Patches

This was resolved in https://github.com/directus/directus/pull/12020 which is released in 9.7.0

### Workarounds

You can disable the live embed in the WYSIWYG by adding `{ "media_live_embeds": false }` to the _Options Overrides_ option of the Rich Text HTML interface.

### References

https://github.com/directus/directus/pull/12020

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [directus/directus](https://github.com/directus/directus)
* Email us at [security@directus.io](mailto:security@directus.io)

## References
- https://github.com/directus/directus/security/advisories/GHSA-xmjj-3c76-5w84
- https://nvd.nist.gov/vuln/detail/CVE-2022-24814
- https://github.com/directus/directus/pull/12020
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v9.7.0
