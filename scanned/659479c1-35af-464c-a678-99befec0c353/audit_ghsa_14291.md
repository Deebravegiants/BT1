# [M] Improper header name validation in guzzlehttp/psr7

## Summary
Severity: Medium
Advisory: GHSA-wxmh-65f7-jcvw
CVE: CVE-2023-29197
CWE: CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-19
Source: https://github.com/advisories/GHSA-wxmh-65f7-jcvw
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/psr7` — affected >=0 <1.9.1
- Packagist: `guzzlehttp/psr7` — affected >=2.0.0 <2.4.5

## Details
### Impact

Improper header parsing. An attacker could sneak in a newline (`\n`) into both the header names and values. While the specification states that `\r\n\r\n` is used to terminate the header list, many servers in the wild will also accept `\n\n`.

### Patches

The issue is patched in 1.9.1 and 2.4.5.

### Workarounds

There are no known workarounds.

### References

* https://www.rfc-editor.org/rfc/rfc7230#section-3.2.4

## References
- https://github.com/guzzle/psr7/security/advisories/GHSA-q7rv-6hp3-vh96
- https://github.com/guzzle/psr7/security/advisories/GHSA-wxmh-65f7-jcvw
- https://nvd.nist.gov/vuln/detail/CVE-2023-29197
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=2022-24775
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/psr7/CVE-2023-29197.yaml
- https://github.com/guzzle/psr7
- https://lists.debian.org/debian-lts-announce/2023/12/msg00028.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FJANWDXJZE5BGLN4MQ4FEHV5LJ6CMKQF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/O35UN4IK6VS2LXSRWUDFWY7NI73RKY2U
- https://www.rfc-editor.org/rfc/rfc7230#section-3.2.4
