# [M] Directus vulnerable to unhandled exception on illegal filename_disk value

## Summary
Severity: Medium
Advisory: GHSA-77qm-wvqq-fg79
CVE: CVE-2022-36031
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-77qm-wvqq-fg79
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <9.15.0

## Details
The Directus process can be aborted by having an authorized user update the `filename_disk` value to a folder and accessing that file through the `/assets` endpoint. 

The vulnerability is patched and released in v9.15.0.

You can prevent this problem by making sure no (untrusted) non-admin users have permissions to update the `filename_disk` field on `directus_files`.

### For more information

If you have any questions or comments about this advisory:
* Open a Discussion in [directus/directus](https://github.com/directus/directus/discussions)
* Email us at [security@directus.io](mailto:security@directus.io)

### Credits

This vulnerability was first discovered and reported by Witold Gorecki.

## References
- https://github.com/directus/directus/security/advisories/GHSA-77qm-wvqq-fg79
- https://nvd.nist.gov/vuln/detail/CVE-2022-36031
- https://github.com/directus/directus
