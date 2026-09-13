# [H] Phar unserialization vulnerability in phpMussel

## Summary
Severity: High
Advisory: GHSA-qr95-4mq5-r3fh
CVE: CVE-2020-4043
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-qr95-4mq5-r3fh
Type: github-advisory

## Affected
- Packagist: `phpmussel/phpmussel` — affected >=1.0.0 <1.6.0
- Packagist: `maikuolan/phpmussel` — affected >=1.0.0 <1.6.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Anyone using >= v1.0.0 < v1.6.0.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Yes. Upgrading to at least >= v1.6.0 (the earliest safe version) will resolve the problem. However, as multiple new major versions have been released since that version, upgrading to the latest available version is recommended, in order to protect against any potential future vulnerabilities, unknown at the time of writing this advisory.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Yes. In the package's configuration, disable archive checking by setting `check_archives` to `false` (thus avoiding execution of the affected parts of the codebase entirely).

### References
_Are there any links users can visit to find out more?_

Yes. The vulnerability is documented at [SECURITY.md](https://github.com/phpMussel/phpMussel/security/policy) and also at [#167](https://github.com/phpMussel/phpMussel/issues/167).

### For more information
If you have any questions or comments about this advisory:
* Comment at the issue linked to this advisory, or..
* Contact [the package author](https://github.com/Maikuolan).

## References
- https://github.com/phpMussel/phpMussel/security/advisories/GHSA-qr95-4mq5-r3fh
- https://nvd.nist.gov/vuln/detail/CVE-2020-4043
- https://github.com/phpMussel/phpMussel/issues/167
- https://github.com/phpMussel/phpMussel/pull/173
- https://github.com/phpMussel/phpMussel/commit/97f25973433921c1f953430f32d3081adc4851a4
- https://github.com/phpMussel/phpMussel
- https://github.com/phpMussel/phpMussel/security/policy#currently-known-vulnerabilities
