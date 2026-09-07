# [H] Reflected XSS when using flashMessages or languageDictionary

## Summary
Severity: High
Advisory: GHSA-jr3j-whm4-9wwm
CVE: CVE-2021-32641
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-04
Source: https://github.com/advisories/GHSA-jr3j-whm4-9wwm
Type: github-advisory

## Affected
- npm: `auth0-lock` — affected >=0 <11.30.1

## Details
### Overview

Versions before and including `11.30.0` are vulnerable to reflected XSS.  An attacker can execute arbitrary code when the library's
- `flashMessage` feature is utilized and user input or data from URL parameters is incorporated into the `flashMessage`.
- `languageDictionary` feature is utilized and user input or data from URL parameters is incorporated into the `languageDictionary`.

### Am I affected?
You are affected by this vulnerability if you are using `auth0-lock` version `11.30.0` or lower and all of the following conditions apply:

- You are utilizing `flashMessage` feature.
- User input or data from URL parameters is incorporated into the `flashMessage`.

An example of a vulnerable snippet where query parameters are used to populate the `text` property of a `flashMessage`.
```js
var params = new URLSearchParams(location.search);
var errorMessage = params.get('error__message');
var showParams = {};

if (!!errorMessage === true) {
  showParams.flashMessage = {
    type: 'error',
    text: 'We were unable to log you in. ' + errorMessage,
  };
}

lock.show(showParams);
```

OR

- You are utilizing `languageDictionary` feature.
- User input or data from URL parameters is used in `languageDictionary` properties.

An example of a vulnerable snippet where query parameters are used to populate the `socialLoginInstructions` property of a `languageDictionary`.
```js
var params = new URLSearchParams(location.search);
var instruction = params.get('instruction');

var options = {
  languageDictionary: {
    emailInputPlaceholder: "something@youremail.com",
    title: "title",
    socialLoginInstructions: instruction
  },
};

var lock = new Auth0LockPasswordless(
    CLIENT_ID,
    DOMAIN,
    options
);

lock.show()
```

### How to fix that?
Upgrade to version `11.30.1`.

### Will this update impact my users?
The fix uses [DOMPurify](https://github.com/cure53/DOMPurify) to sanitise the `flashMessage` and `languageDictionary` inputs. If you are including inline JavaScript in these fields, like `script` tags or `onclick` attributes, these will be removed.

## References
- https://github.com/auth0/lock/security/advisories/GHSA-jr3j-whm4-9wwm
- https://nvd.nist.gov/vuln/detail/CVE-2021-32641
- https://github.com/auth0/lock/commit/d139cf01c8234b07caf265e051f39d3eab08f7ed
- https://github.com/auth0/lock/releases/tag/v11.30.1
