# [M] Kirby CMS's content locks disclose IDs and emails of inaccessible users from `users.access/list` permissions

## Summary
Severity: Medium
Advisory: GHSA-39vq-49qm-r2mc
CVE: CVE-2026-45334
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-39vq-49qm-r2mc
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.1
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.1

## Details
### TL;DR

This vulnerability affects all Kirby sites that restrict the visibility of users for certain roles via the `users.access` or `users.list` permissions. A site is affected if users of a particular role are not allowed to see other users in the Panel, for example because the role's blueprint sets `users.access: false` or `users.list: false` as permission for the authenticated user role and/or as option for the target user role.

A Kirby site is *not* affected if all authenticated Panel users are permitted to access and list other users. The vulnerability can only be exploited by authenticated users.

---

### Introduction

Missing authorization allows authenticated users to gain access to information they are not intended to see.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Affected components

Kirby's user permissions control which user role is allowed to perform specific actions or access specific information in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). The `users.access` and `users.list` permissions control whether users of a given role are allowed to access and list other users in the Panel. It is also possible to customize the permissions for each target role using the `options` feature. The permissions and options together control the authorization of user actions.

Kirby's Panel includes a content-locking feature that records which user currently has a model open for editing. This lock prevents conflicting edits by multiple users and displays the locking user's identity in the Panel UI so other users know who to contact. Internally, the locking user's email address and identifier are included in every Panel view payload and in error responses returned when a user attempts to edit a model that is currently locked by another user.

### Impact

In affected releases, this lock information was returned without checking whether the requesting user had permission to access or list the locking user.

This allowed a low-privilege authenticated Panel user, whose role was configured with `users.access: false` or `users.list: false`, to learn the email address and identifier of any user who currently had a model open for editing in the Panel, including administrators and other higher-privilege users. Content locks are active for a configurable window (10 minutes by default).

The email address can allow to enumerate admin accounts, target phishing, and feed credential-stuffing attacks against the Kirby installation or other sites.

The internal user ID can be cross-referenced with other endpoints once the requester has obtained a higher privilege through unrelated means.

### Patches

The problem has been patched in [Kirby 4.9.1](https://github.com/getkirby/kirby/releases/tag/4.9.1) and [Kirby 5.4.1](https://github.com/getkirby/kirby/releases/tag/5.4.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In the mentioned releases, the lock information is now filtered based on the requesting user's permissions. The identity of the locking user is hidden when the requesting user does not have permission to access or list that user.

### Credits

Kirby thanks Matteo Panzeri (@matte1782) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-39vq-49qm-r2mc
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.1
- https://github.com/getkirby/kirby/releases/tag/5.4.1
