# [H] Kirby: File upload permissions are not checked during processing of chunk data

## Summary
Severity: High
Advisory: GHSA-67mx-6wf2-92xp
CVE: CVE-2026-71415
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-31
Source: https://github.com/advisories/GHSA-67mx-6wf2-92xp
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.5.2

## Details
### TL;DR

This vulnerability affects all Kirby sites where users of a particular role have access to the REST API (`access.panel` permission is enabled) but no permission to upload any kind of file (`files.create`, `files.replace` and `user/users.update` permissions are all disabled).

It was possible to fill up the temporary directory for chunked uploads with unfinished chunks even as a user without any upload permission.

**This vulnerability is of high severity for affected sites.**

Your Kirby sites are *not* affected if you intend all users of your site to be able to upload files. The vulnerability can only be exploited by authenticated users. It was *not* possible to bypass the actual permission checks for any files that end up in the `content` or `site/accounts` folders.

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Affected components

Kirby's REST API provides routes to upload files, specifically to create content files, replace existing content files and to create and replace user avatars.

Each upload route takes either full file upload requests or chunked upload requests that can be continued in subsequent requests.
During a chunked upload, the incomplete state of the uploaded file is stored in a temporary directory until the last chunk completes the file. At this time, the final permission and business logic checks are performed before the complete file is moved to its final destination.

### Impact

In affected releases, the chunk upload handler did not check for the user's file upload permissions before storing incomplete chunk data in the temporary directory.

This allowed attackers without upload permissions to upload multiple large files in chunks. If the final chunk was never provided, Kirby would keep the incomplete files for 24 hours. This could cause attacker-controlled storage consumption until the temporary files were automatically cleaned up or manually removed, potentially preventing other users from uploading files, or site logic from storing data.

### Patches

The problem has been patched in [Kirby 5.5.2](https://github.com/getkirby/kirby/releases/tag/5.5.2). Please update this or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have added preflight checks to the upload chunk processor that verify the relevant system permission before storing the chunk data in the temporary directory.

### Credits

Thanks to @alcls01111 for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-67mx-6wf2-92xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-71415
- https://github.com/getkirby/kirby/pull/8296
- https://github.com/getkirby/kirby/commit/37e206f3ed40ad3fab2e47e055ccb19e9c207dab
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/5.5.2
