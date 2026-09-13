# [M] Script injection

## Summary
Severity: Medium
Advisory: GHSA-gg96-f8wr-p89f
CVE: CVE-2021-32661
CWE: CWE-434, CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-04
Source: https://github.com/advisories/GHSA-gg96-f8wr-p89f
Type: github-advisory

## Affected
- npm: `@backstage/plugin-techdocs` — affected >=0 <0.9.5

## Details
### Impact

A malicious internal actor can potentially upload documentation content with malicious scripts by embedding the script within an `object` element. This may give access to sensitive data when other users visit that same documentation page.

The ability to upload malicious content may be limited by internal code review processes, unless the chosen TechDocs deployment method is to use an object store and the actor has access to upload files directly to that store.

### Patches

The vulnerability is patched in the `0.9.5` release of `@backstage/plugin-techdocs`.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
* Visit our chat, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-gg96-f8wr-p89f
- https://nvd.nist.gov/vuln/detail/CVE-2021-32661
- https://github.com/backstage/backstage/commit/aad98c544e59369901fe9e0a85f6357644dceb5c
- https://github.com/backstage/backstage/releases/tag/release-2021-06-03
