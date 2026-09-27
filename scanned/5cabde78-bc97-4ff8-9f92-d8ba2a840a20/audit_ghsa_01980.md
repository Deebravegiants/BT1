# [M] Script injection

## Summary
Severity: Medium
Advisory: GHSA-pwhf-39xg-4rxw
CVE: CVE-2021-32660
CWE: CWE-434, CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-04
Source: https://github.com/advisories/GHSA-pwhf-39xg-4rxw
Type: github-advisory

## Affected
- npm: `@backstage/techdocs-common` — affected >=0 <0.6.4

## Details
### Impact

A malicious internal actor is able to upload documentation content with malicious scripts. These scripts would normally be sanitized by the TechDocs frontend, but by tricking a user to visit the content via the TechDocs API, the content sanitazion will be bypassed. If the TechDocs API is hosted on the same origin as the Backstage app or other backend plugins, this may give access to sensitive data.

The ability to upload malicious content may be limited by internal code review processes, unless the chosen TechDocs deployment method is to use an object store and the actor has access to upload files directly to that store.

### Patches

The vulnerability is patched in the `0.6.4` release of `@backstage/techdocs-common`.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
* Visit our chat, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-pwhf-39xg-4rxw
- https://nvd.nist.gov/vuln/detail/CVE-2021-32660
- https://github.com/backstage/backstage/commit/aad98c544e59369901fe9e0a85f6357644dceb5c
- https://github.com/backstage/backstage/releases/tag/release-2021-06-03
