# [H] Improper Restriction of Excessive Authentication Attempts in Sorcery

## Summary
Severity: High
Advisory: GHSA-jc8m-cxhj-668x
CVE: CVE-2020-11052
CWE: CWE-307
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2020-05-07
Source: https://github.com/advisories/GHSA-jc8m-cxhj-668x
Type: github-advisory

## Affected
- RubyGems: `sorcery` — affected >=0 <0.15.0

## Details
### Impact
Brute force vulnerability when using password authentication via Sorcery. The brute force protection submodule will prevent a brute force attack for the defined lockout period, but once expired protection will not be re-enabled until a user or malicious actor logs in successfully. This does not affect users that do not use the built-in brute force protection submodule, nor users that use permanent account lockout.

### Patches
Patched as of version `0.15.0`.

### Workarounds
Currently no workarounds, other than monkey patching the authenticate method provided by Sorcery or upgrading to version `0.15.0`.

## References
- https://github.com/Sorcery/sorcery/security/advisories/GHSA-jc8m-cxhj-668x
- https://nvd.nist.gov/vuln/detail/CVE-2020-11052
- https://github.com/Sorcery/sorcery/issues/231
- https://github.com/Sorcery/sorcery/pull/235
- https://github.com/Sorcery/sorcery/commit/0f116d223826895a73b12492f17486e5d54ab7a7
- https://github.com/Sorcery/sorcery
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sorcery/CVE-2020-11052.yml
