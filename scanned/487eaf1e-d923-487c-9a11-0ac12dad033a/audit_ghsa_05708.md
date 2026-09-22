# [M] Kirby is missing permission checks in the content changes API

## Summary
Severity: Medium
Advisory: GHSA-4j78-4xrm-cr2f
CVE: CVE-2026-21896
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-4j78-4xrm-cr2f
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.2.2

## Details
### TL;DR

This vulnerability affects all Kirby sites where user permissions are configured to prevent specific role(s) from performing write actions, specifically by disabling the `update` permission with the intent to prevent modifications to site content.

If developers haven't configured any user permissions that deviate from the default of allowing all actions, their site is *not* affected.

----

### Introduction

Kirby allows to restrict the permissions of specific user roles. Users of that role can only perform permitted actions.

Permissions for updating content have already existed and could be configured for each model type, but were not enforced by Kirby's API backend code during operations to the changes version.

The changes version is the content version that contains unsaved changes of existing models (pages, users, files or the site).

### Impact

The missing permission checks allowed attackers with Panel access to create or discard a changes version or update the content fields in an existing changes version. All of these actions could affect arbitrary models.

This could cause the following impact:

- Attackers could maliciously create changes versions for all models of the site, creating editing locks that would prevent other authenticated users from making content changes until those locks were cleared.
- Attackers could update the content in a malicious way, for example by adding defamatory or spam content or by including malicious links or scripts. While this updated content would not immediately be published to the site, an inattentive editor with update permissions could inadvertently publish these changes in the belief that an authorized user has made them.
- Attackers could discard extensive changes, making editors lose their content work.

### Patches

The problem has been patched in [Kirby 5.2.2](https://github.com/getkirby/kirby/releases/tag/5.2.2). Please update to this or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In the mentioned release, we have added checks for the model `update` permissions that ensure that users without this permission cannot create, edit or discard the changes version of the respective model.

A future Kirby release will add separate `edit` and `save` permissions that will make it possible to control write actions to model content more granularly.

### Credits

Thanks to Lukas Kleinschmidt (@lukaskleinschmidt) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-4j78-4xrm-cr2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-21896
- https://github.com/getkirby/kirby/commit/f5ce1347b427b819bf193acf11fd0da232f7af47
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/5.2.2
