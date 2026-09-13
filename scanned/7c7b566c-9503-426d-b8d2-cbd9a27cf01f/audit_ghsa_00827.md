# [C] Potential Command Injection in libnotify

## Summary
Severity: Critical
Advisory: GHSA-6898-wx94-8jq8
CVE: CVE-2013-7381
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-6898-wx94-8jq8
Type: github-advisory

## Affected
- npm: `libnotify` — affected >=0 <1.0.4

## Details
Versions 1.0.3 and earlier of libnotify are affected by a shell command injection vulnerability. This may result in execution of arbitrary shell commands, if user input is passed into libnotify.notify.

Untrusted input passed in the call to libnotify.notify could result in execution of shell commands. Callers may be unaware of this.

### Example
```js
var libnotify = require('libnotify')
libnotify.notify('UNTRUSTED INPUT', { title: \"\" }, function () {
    console.log(arguments);
})
```

Special thanks to Neal Poole for submitting the pull request to fix this issue.


## Recommendation

Update to version 1.0.4 or greater

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7381
- https://github.com/mytrile/node-libnotify/commit/dfe7801d73a0dda10663a0ff3d0ec8b4d5f0d448
- https://github.com/mytrile/node-libnotify
- https://www.npmjs.com/advisories/20
- http://www.openwall.com/lists/oss-security/2014/05/13/1
- http://www.openwall.com/lists/oss-security/2014/05/15/2
