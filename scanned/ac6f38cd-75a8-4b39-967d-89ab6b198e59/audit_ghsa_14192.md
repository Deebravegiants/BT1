# [M] Insecure header validation in slim/psr7

## Summary
Severity: Medium
Advisory: GHSA-q2qj-628g-vhfw
CVE: CVE-2023-30536
CWE: CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-04-18
Source: https://github.com/advisories/GHSA-q2qj-628g-vhfw
Type: github-advisory

## Affected
- Packagist: `slim/psr7` — affected >=1.6 <1.6.1
- Packagist: `slim/psr7` — affected >=1.5 <1.5.1
- Packagist: `slim/psr7` — affected >=0 <1.4.1

## Details
### Impact

An attacker could sneak in a newline (`\n`) into both the header names and values. While the specification states that `\r\n\r\n` is used to terminate the header list, many servers in the wild will also accept `\n\n`. An attacker that is able to control the header names that are passed to Slilm-Psr7 would be able to intentionally craft invalid messages, possibly causing application errors or invalid HTTP requests being sent out with an PSR-18 HTTP client. The latter might present a denial of service vector if a remote service’s web application firewall bans the application due to the receipt of malformed requests.

### Patches

The issue is patched in 1.6.1, 1.5.1, and 1.4.1.

### Workarounds

In Slim-Psr7 prior to 1.6.1, 1.5.1, and 1.4.1, validate HTTP header keys and/or values, and if using user-supplied values, filter them to strip off leading or trailing newline characters before calling withHeader().

### Acknowledgments

We are very grateful to and thank <a href="https://gjcampbell.co.uk/">Graham Campbell</a> for reporting and working with us on this issue.

### References

* Guzzle: CVE-2023-29197, with advisory GHSA-wxmh-65f7-jcvw
* Laminas Diactoros: CVE-2023-29530, with advisory GHSA-xv3h-4844-9h36
* https://www.rfc-editor.org/rfc/rfc7230#section-3.2.4

## References
- https://github.com/slimphp/Slim-Psr7/security/advisories/GHSA-q2qj-628g-vhfw
- https://nvd.nist.gov/vuln/detail/CVE-2023-30536
- https://github.com/slimphp/Slim-Psr7/issues/284#issuecomment-1541328898
- https://github.com/slimphp/Slim-Psr7/commit/ed1d553225dd190875d8814c47460daed4b550bb
- https://github.com/slimphp/Slim-Psr7
- https://github.com/slimphp/Slim-Psr7/releases/tag/1.4.1
- https://github.com/slimphp/Slim-Psr7/releases/tag/1.5.1
- https://github.com/slimphp/Slim-Psr7/releases/tag/1.6.1
- https://www.rfc-editor.org/rfc/rfc7230#section-3.2.4
