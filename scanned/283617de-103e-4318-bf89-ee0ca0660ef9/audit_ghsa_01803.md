# [H] RCE vulnerability affecting v1beta3 templates in @backstage/plugin-scaffolder-backend

## Summary
Severity: High
Advisory: GHSA-2g8g-63j4-9w3r
Ecosystem: npm
Published: 2021-12-01
Source: https://github.com/advisories/GHSA-2g8g-63j4-9w3r
Type: github-advisory

## Affected
- npm: `@backstage/plugin-scaffolder-backend` — affected >=0 <0.15.14

## Details
The templating library used by the scaffolder backend assumes that templates are trusted which is an undesired property of the scaffolder-backend. This has now been mitigated by sandboxing the template code execution.

### Impact
A malicious actor with write access to a registered scaffolder template could manipulate the template in a way that allows for remote code execution on the scaffolder-backend instance. This was only exploitable in the template yaml definition itself and not by user input data.

### Patches
This is vulnerability is patched in version `0.15.14` of `@backstage/plugin-scaffolder-backend`.


### For more information
If you have any questions or comments about this advisory:

* Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
* Visit our chat, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-2g8g-63j4-9w3r
- https://github.com/backstage/backstage
