# [M] Kirby CMS's system API endpoint leaks installed version and license data to authenticated users

## Summary
Severity: Medium
Advisory: GHSA-x68m-c7jf-2572
CVE: CVE-2026-42051
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-x68m-c7jf-2572
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.0
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.0

## Details
### TL;DR

This vulnerability affects all Kirby sites that might have potential attackers in the group of authenticated Panel users.

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Impact

Kirby's user permissions control which user role is allowed to perform specific actions in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). The permissions control the authorization of user actions (with handling of model-specific authorization omitted here for brevity).

Kirby provides the `access.system` permission (among others) that controls access to the system area of the Kirby Panel. This area contains internal system information like the installed Kirby, plugin and server versions, security state and Kirby license. If the `access.system` permission is disabled for a user role, users of that role should not be able to access this internal system information. However it is also possible to access some system information via the `/api/system` REST API endpoint. In affected releases, the response of this endpoint for authenticated users contained the installed Kirby version and the status, type and code of the installed Kirby license. These values are considered sensitive information and should be protected by the `access.system` permission.

The installed Kirby version and license data can be used by malicious actors during reconnaissance when planning a separate attack.

### Patches

The problem has been patched in [Kirby 4.9.0](https://github.com/getkirby/kirby/releases/tag/4.9.0) and [Kirby 5.4.0](https://github.com/getkirby/kirby/releases/tag/5.4.0). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have protected the version and license properties of the `/api/system` endpoint with a check for the existing `access.system` permission. This ensures that the REST API only outputs information that should be accessible to the user via the Panel.

### Credits

Kirby thanks @HuajiHD and @0x-bala for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-x68m-c7jf-2572
- https://nvd.nist.gov/vuln/detail/CVE-2026-42051
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.0
- https://github.com/getkirby/kirby/releases/tag/5.4.0
