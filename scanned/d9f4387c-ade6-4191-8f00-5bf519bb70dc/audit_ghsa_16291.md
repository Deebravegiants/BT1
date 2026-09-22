# [C] Pixelfed doesn't check OAuth Scopes in API routes, giving elevated permissions

## Summary
Severity: Critical
Advisory: GHSA-gccq-h3xj-jgvf
CVE: CVE-2024-25108
CWE: CWE-280, CWE-285, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-02-12
Source: https://github.com/advisories/GHSA-gccq-h3xj-jgvf
Type: github-advisory

## Affected
- Packagist: `pixelfed/pixelfed` — affected >=0.10.4 <0.11.11

## Details
### Summary

When processing requests authorization was improperly and insufficiently checked, allowing attackers to access far more functionality than users intended, including to the administrative and moderator functionality of the Pixelfed server.

This vulnerability affects every version of Pixelfed between `v0.10.4` and `v0.11.9`, inclusive. A proof of concept of this vulnerability exists.

### Details

In vulnerable versions of Pixelfed (versions before 0.11.11), when the API checked the request for permissions to perform a certain behavior, it did not check that the OAuth Application/Client had granted access to those API endpoints, it only checked if the user was authenticated via an access token, and if the user was the owner of the resource or an admin on the instance.

This meant that an attacker could request an access token for "read" permissions to authenticate you with their application, but the access token that they obtained actually could be used for "write" or even administrative actions, and the user who granted access to their account had zero knowledge of this elevated access.

#### Proof of Concept

1. Create an access token either via [2-legged OAuth flow](https://oauth.net/2/grant-types/authorization-code/) for the `read` scope, or create a Personal Access Tokens with the `read` scope.
2. Using that Access Token, perform a request that would need a particular higher-privilege scope, for instance, following a user or performing an administrative request. (respectively requiring `follow` or `admin:read` and `admin:write` scopes in the patched versions)
3. Observe that despite your access token having `read` permissions, the follow or administrative request was successful.

e.g., Maybe an attacker collects an access token (which expires in 1 year) wants to do something really nasty to an admin, such as disabling federation on their target's pixelfed server. As long as that server has `instance.enable_cc` configured (defaults to `true`), then the attacker can use the `read` scoped access token and perform the following request:

```
POST /api/admin/config/update
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access token with read scope>

{ "key": "federation.activitypub.enabled": "value": false }
```

And federation of that pixelfed server would be subsequently disabled, as if the administrator had disabled it.

### Impact

This vulnerability affects every local user of a Pixelfed server, and can potentially affect the servers' ability to federate.

Some user interaction is required to setup the conditions to be able to exercise the vulnerability, but the attacker could conduct this attack time-delayed manner, where user interaction is not actively required, since access tokens in Pixelfed have a 1-year lifetime before they expire, and users' often forget to revoke access tokens for applications that they are no longer using.

This also means that Access Tokens that may have been leaked from third-party OAuth Application's databases would be usable for a significant amount of time by potential attackers.

### Prior versions

Whilst this vulnerability is listed as `>= 0.10.4`, there is potential that versions before `0.10.4` are also vulnerable to this sort of security bypass, however, given that the code changed significantly between `0.10.3` and `0.10.4` we've been unable to easily assess if these heavily outdated versions are vulnerable or not to this exploit.

### Sponsorship

The work involved in investigating and remediation of this security vulnerability was provided by [Nivenly Foundation](https://nivenly.org/), for whom we are grateful for their support of the Fediverse and Pixelfed.

## References
- https://github.com/pixelfed/pixelfed/security/advisories/GHSA-gccq-h3xj-jgvf
- https://nvd.nist.gov/vuln/detail/CVE-2024-25108
- https://github.com/pixelfed/pixelfed/commit/7e47d6dccb0393a2e95c42813c562c854882b037
- https://github.com/pixelfed/pixelfed/commit/fd7f5dbb
- https://github.com/pixelfed/pixelfed/commit/fd7f5dbba13818f60d1c2b3ab110b499e996aa81
- https://github.com/pixelfed/pixelfed
