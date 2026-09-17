# [C] Potential Code Injection in Sprout Forms

## Summary
Severity: Critical
Advisory: GHSA-px8v-hxxx-2rgh
CVE: CVE-2020-11056
CWE: CWE-74, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2020-05-08
Source: https://github.com/advisories/GHSA-px8v-hxxx-2rgh
Type: github-advisory

## Affected
- Packagist: `barrelstrength/sprout-base-email` — affected >=0 <1.2.7
- Packagist: `barrelstrength/sprout-forms` — affected >=0 <3.9.0

## Details
### Impact

A potential Server-Side Template Injection vulnerability exists in Sprout Forms which could lead to the execution of Twig code.

### Patches

The problem is fixed in`barrelstrength/sprout-forms:v3.9.0` which upgrades to `barrelstrength/sprout-base-email:v1.2.7`

### Workarounds

Users unable to upgrade should update any Notification Emails to use the "Basic Notification (Sprout Email)" template and avoid using the "Basic Notification (Sprout Forms)" template or any custom templates that display Form Fields.

### References

- See the release notes in the [CHANGELOG](https://github.com/barrelstrength/craft-sprout-forms/blob/v3/CHANGELOG.md#390---2020-04-09-critical)
- Credits to Paweł Hałdrzyński, Daniel Kalinowski from [ISEC.PL](https://isec.pl/) for discovery and responsible disclosure

### For more information

If you have any questions or comments about this advisory:

* Open an issue in the [Sprout Forms repo](https://github.com/barrelstrength/craft-sprout-forms/issues)
* Email us at [sprout@barrelstrengthdesign.com](mailto:sprout@barrelstrengthdesign.com)

## References
- https://github.com/barrelstrength/craft-sprout-forms/security/advisories/GHSA-px8v-hxxx-2rgh
- https://nvd.nist.gov/vuln/detail/CVE-2020-11056
- https://github.com/barrelstrength/craft-sprout-base-email/commit/5ef759f4713ede6dbf77c9d9df9f992876e43a49
- https://github.com/barrelstrength/craft-sprout-forms/blob/v3/CHANGELOG.md#390---2020-04-09-critical
