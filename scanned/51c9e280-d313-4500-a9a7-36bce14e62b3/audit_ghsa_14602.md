# [M] Path Traversal Vulnerability in `LESS` Parser allows reading of sensitive server files

## Summary
Severity: Medium
Advisory: GHSA-vhm8-wwrf-3gcw
CVE: CVE-2023-27577
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-03-13
Source: https://github.com/advisories/GHSA-vhm8-wwrf-3gcw
Type: github-advisory

## Affected
- Packagist: `flarum/core` — affected >=0 <1.7.0

## Details
### Impact
If an admin account has already been compromised by an attacker, the `LESS` parser can be exploited to read sensitive files on the server through the use of path traversal techniques.

An attacker can achieve this by providing an absolute path to a sensitive file in the custom `LESS` setting, which the `LESS` parser will then read. For example, an attacker could use the following code to read the contents of the `/etc/passwd` file:

```less
@import (inline) '/etc/passwd';

.test {
  content: data-uri('/etc/passwd');
}
```

### Patches
The vulnerability has been addressed in version `1.7`. Users should upgrade to this version to mitigate the vulnerability.

### Workarounds
Users can mitigate the vulnerability by ensuring that their admin accounts are secured with strong passwords and other best practices for account security. Additionally, users can limit the exposure of sensitive files on the server by implementing appropriate file permissions and access controls.

## References
- https://github.com/flarum/framework/security/advisories/GHSA-vhm8-wwrf-3gcw
- https://nvd.nist.gov/vuln/detail/CVE-2023-27577
- https://github.com/flarum/framework/commit/1761660c98ea5a3e9665fb8e6041d1f2ee62a444
- https://github.com/flarum/flarum-core
- https://github.com/flarum/flarum-core/releases/tag/v1.7.0
