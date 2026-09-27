# [H] HTTP Multiline Header Termination

## Summary
Severity: High
Advisory: GHSA-xv3h-4844-9h36
CVE: CVE-2023-29530
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-xv3h-4844-9h36
Type: github-advisory

## Affected
- Packagist: `laminas/laminas-diactoros` — affected >=0 <2.18.1
- Packagist: `laminas/laminas-diactoros` — affected >=2.19.0 <2.19.1
- Packagist: `laminas/laminas-diactoros` — affected >=2.20.0 <2.20.1
- Packagist: `laminas/laminas-diactoros` — affected >=2.21.0 <2.21.1
- Packagist: `laminas/laminas-diactoros` — affected >=2.22.0 <2.22.1
- Packagist: `laminas/laminas-diactoros` — affected >=2.23.0 <2.23.1
- Packagist: `laminas/laminas-diactoros` — affected >=2.24.0 <2.24.2
- Packagist: `laminas/laminas-diactoros` — affected >=2.25.0 <2.25.2

## Details
### Impact

Affected versions of Laminas Diactoros accepted a single line feed (LF / `\n` ) character at the end of a header name. When serializing such a header name containing a line-feed into the on-the-wire representation of a HTTP/1.x message, the resulting message would be syntactically invalid, due to the header line being terminated too early. An attacker that is able to control the header names that are passed to Laminas Diactoros would be able to intentionally craft invalid messages, possibly causing application errors or invalid HTTP requests being sent out with an PSR-18 HTTP client. The latter might present a denial of service vector if a remote service’s web application firewall bans the application due to the receipt of malformed requests.

### Patches

The problem has been patched in the following versions:

- 2.18.1
- 2.19.1
- 2.20.1
- 2.21.1
- 2.22.1
- 2.23.1
- 2.24.2
- 2.25.2

### Workarounds

Validate HTTP header keys and/or values, and if using user-supplied values, filter them to strip off leading or trailing newline characters before calling `withHeader()`.

### References

- CVE-2023-29197
- GHSA-wxmh-65f7-jcvw

## References
- https://github.com/laminas/laminas-diactoros/security/advisories/GHSA-xv3h-4844-9h36
- https://nvd.nist.gov/vuln/detail/CVE-2023-29530
- https://github.com/laminas/laminas-diactoros/commit/7e721a60a09c5119c98694c2d23fc031094e1f1c
- https://github.com/advisories/GHSA-wxmh-65f7-jcvw
- https://github.com/laminas/laminas-diactoros
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BPW54QK7ISDALPLP2CKODU4ZIVRYS336
