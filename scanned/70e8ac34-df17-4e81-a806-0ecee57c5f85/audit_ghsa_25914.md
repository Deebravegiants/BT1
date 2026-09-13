# [M] Improper Input Validation in guzzlehttp/psr7

## Summary
Severity: Medium
Advisory: GHSA-q7rv-6hp3-vh96
CVE: CVE-2022-24775
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-25
Source: https://github.com/advisories/GHSA-q7rv-6hp3-vh96
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/psr7` — affected >=0 <1.8.4
- Packagist: `guzzlehttp/psr7` — affected >=2.0.0 <2.1.1

## Details
### Impact

Improper header parsing. An attacker could sneak in a carriage return character (`\r`) and pass untrusted values in both the header names and values.

### Patches

The issue is patched in 1.8.4 and 2.1.1.

### Workarounds

There are no known workarounds.

### References

* https://www.rfc-editor.org/rfc/rfc7230#section-3.2.4

## References
- https://github.com/guzzle/psr7/security/advisories/GHSA-q7rv-6hp3-vh96
- https://nvd.nist.gov/vuln/detail/CVE-2022-24775
- https://github.com/guzzle/psr7/pull/485/commits/e55afaa3fc138c89adf3b55a8ba20dc60d17f1f1
- https://github.com/guzzle/psr7/pull/486/commits/9a96d9db668b485361ed9de7b5bf1e54895df1dc
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/psr7/CVE-2022-24775.yaml
- https://github.com/guzzle/psr7
- https://www.drupal.org/sa-core-2022-006
- https://www.rfc-editor.org/rfc/rfc7230#section-3.2.4
