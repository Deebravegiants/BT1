# [M] Firefly III has a MFA bypass in oauth flow

## Summary
Severity: Medium
Advisory: GHSA-4gm4-c4mh-4p7w
CVE: CVE-2024-37893
CWE: CWE-287, CWE-288
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-4gm4-c4mh-4p7w
Type: github-advisory

## Affected
- Packagist: `grumpydictator/firefly-iii` — affected >=0 <6.1.17

## Details
### Impact

A MFA bypass in the Firefly III OAuth flow may allow malicious users to bypass the MFA-check. This allows malicious users to use password spraying to gain access to your Firefly III data using passwords stolen from other sources. As OAuth applications are easily enumerable using an incrementing id, an attacker could try sign an OAuth application up to a users profile quite easily if they have created one. The attacker would also need to know the victims username and password.

### Patches

Problem has been patched in Firefly III v6.1.17 and up.

### Workarounds

- Use a unique password for your Firefly III instance,
- Store your password securely, i.e. in a password manager or in your head.

### References

- https://owasp.org/www-community/attacks/Password_Spraying_Attack
- https://www.menlosecurity.com/what-is/highly-evasive-adaptive-threats-heat/mfa-bypass

## References
- https://github.com/firefly-iii/firefly-iii/security/advisories/GHSA-4gm4-c4mh-4p7w
- https://nvd.nist.gov/vuln/detail/CVE-2024-37893
- https://github.com/firefly-iii/firefly-iii
- https://owasp.org/www-community/attacks/Password_Spraying_Attack
- https://www.menlosecurity.com/what-is/highly-evasive-adaptive-threats-heat/mfa-bypass
