# [M] auth0-lock vulnerable to XSS via unsanitized placeholder property

## Summary
Severity: Medium
Advisory: GHSA-w2pf-g6r8-pg22
CVE: CVE-2019-20174
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-01-31
Source: https://github.com/advisories/GHSA-w2pf-g6r8-pg22
Type: github-advisory

## Affected
- npm: `auth0-lock` — affected >=0 <11.21.0

## Details
## Overview

Auth0 Lock version 11.20.4 and earlier did not properly sanitize the generated HTML code. Customers using the `additionalSignUpFields` customization option to add a checkbox to the sign-up dialog that are passing a `placeholder` property obtained from an untrusted source (e.g. a query parameter) could allow cross-site scripting (XSS) on their signup pages.

## Am I affected?

You are affected by this vulnerability if all of the following conditions apply:

- You are using Auth0 Lock version 11.20.4 or earlier.
- You pass `additionalSignUpFields` as options when initializing Lock which includes a field of type `checkbox` whose `placeholder` value is obtained from an untrusted source.

An example of a vulnerable snippet is the following where the `placeholder` value is partially user-controlled by the `name` query parameter:

```javascript
<script>
    var params = new URLSearchParams(window.location.search);
    var options = {
        auth: {
            redirectUrl: 'http://localhost:12345/callback',
            responseType: 'code',
            params: {
                scope: 'openid email',
            },
        },
        additionalSignUpFields: [{
            name: 'agree',
            type: 'checkbox',
            placeholder: "I agree to Terms and Conditions for " + params.get('name'),
        }],
    };
    var lock = new Auth0Lock('<CLIENT_ID>', '<TENANT_NAME>.auth0.com', options);
    lock.show({
        allowShowPassword: true,
        initialScreen: 'signUp',
    });
</script>
```

## How to fix that?

Developers using Auth0’s signin solution Lock need to upgrade to version 11.21.0 or later. Version 11.21.0 introduces two changes:

1. The existing `placeholder` property is now treated as plain text to mitigate the problem.
2. A new `placeholderHTML` property is introduced that indicates the level of control it provides and that it should be only supplied from trusted sources.

## Will this update impact my users?

This fix patches the Auth0 Lock widget and may require changes in application code, but it will not impact your users, their current state, or any existing sessions.

Developers using the `placeholder` property with HTML content from a trusted source should start using the `placeholderHTML` property to continue providing the same user experience.

## References
- https://github.com/auth0/lock/security/advisories/GHSA-w2pf-g6r8-pg22
- https://nvd.nist.gov/vuln/detail/CVE-2019-20174
- https://github.com/auth0/lock/commit/6c15e5659c21cd814ea119af5c51b61399598dd5
- https://auth0.com/docs/security/bulletins/cve-2019-20174
- https://github.com/auth0/lock/releases/tag/v11.21.0
