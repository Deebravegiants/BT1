# [C] Authentication Bypass by CSRF Weakness 

## Summary
Severity: Critical
Advisory: GHSA-5629-8855-gf4g
CWE: CWE-305, CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-11-18
Source: https://github.com/advisories/GHSA-5629-8855-gf4g
Type: github-advisory

## Affected
- RubyGems: `solidus_core` — affected >=0 <2.11.12
- RubyGems: `solidus_core` — affected >=3.0.0 <3.0.3
- RubyGems: `solidus_core` — affected >=3.1.0 <3.1.3

## Details
### Impact
The actual vulnerability has been discovered on `solidus_auth_devise`. See [GHSA-xm34-v85h-9pg2](https://github.com/solidusio/solidus_auth_devise/security/advisories/GHSA-xm34-v85h-9pg2) for details.

The security advisory here exists to provide an extra layer of security in the form of a monkey patch for users who don't update `solidus_auth_devise`. For this reason, it has been marked as low impact on this end.

### Patches
For extra security, update `solidus_core` to versions `3.1.3`, `3.0.3` or `2.11.12`.

### Workarounds
Look at the workarounds described at [GHSA-xm34-v85h-9pg2](https://github.com/solidusio/solidus_auth_devise/security/advisories/GHSA-xm34-v85h-9pg2).

### References
- [GHSA-xm34-v85h-9pg2](https://github.com/solidusio/solidus_auth_devise/security/advisories/GHSA-xm34-v85h-9pg2).

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [solidus_auth_devise](https://github.com/solidusio/solidus_auth_devise/issues) or a discussion in [solidus](https://github.com/solidusio/solidus/discussions)
* Email us at [security@solidus.io](mailto:security@soliidus.io)
* Contact the core team on [Slack](http://slack.solidus.io/)

## References
- https://github.com/solidusio/solidus/security/advisories/GHSA-5629-8855-gf4g
- https://github.com/solidusio/solidus_auth_devise/security/advisories/GHSA-xm34-v85h-9pg2
- https://github.com/solidusio/solidus
