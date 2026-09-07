# [C] XSS vulnerability with translator

## Summary
Severity: Critical
Advisory: GHSA-5qjq-69w6-fg57
CVE: CVE-2021-32671
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-07
Source: https://github.com/advisories/GHSA-5qjq-69w6-fg57
Type: github-advisory

## Affected
- Packagist: `flarum/core` — affected >=1.0.0 <1.0.2

## Details
Flarum's translation system allowed for string inputs to be converted into HTML DOM nodes when rendered. This change was made after v0.1.0-beta.16 (our last beta before v1.0.0) and was not noticed or documented.

This allowed for any user to type malicious HTML markup within certain user input fields and have this execute on client browsers. The example which led to the discovery of this vulnerability was in the forum search box. Entering faux-malicious HTML markup, such as <script>alert('test')</script> resulted in an alert box appearing on the forum. This attack could also be modified to perform AJAX requests on behalf of a user, possibly deleting discussions, modifying their settings or profile, or even modifying settings on the Admin panel if the attack was targetted towards a privileged user.

### Impact

All Flarum communities that run flarum v1.0.0 or v1.0.1 are impacted.

### Patches

The vulnerability has been fixed and published as flarum/core v1.0.2. All communities running Flarum v1.0 have to upgrade as soon as possible to v1.0.2 using:

```
composer update --prefer-dist --no-dev -a -W
```

You can then confirm you run the latest version using:

```
composer show flarum/core
```

### Workarounds

__None.__

### For more information

For any questions or comments on this vulnerability please visit https://discuss.flarum.org/d/27558.

For support questions create a discussion at https://discuss.flarum.org/t/support.

A reminder that if you ever become aware of a security issue in Flarum, please report it to us privately by emailing security@flarum.org, and we will address it promptly.

## References
- https://github.com/flarum/core/security/advisories/GHSA-5qjq-69w6-fg57
- https://nvd.nist.gov/vuln/detail/CVE-2021-32671
- https://github.com/flarum/core/commit/440bed81b8019dff00642c8f493b4909d505a28a
- https://packagist.org/packages/flarum/core
