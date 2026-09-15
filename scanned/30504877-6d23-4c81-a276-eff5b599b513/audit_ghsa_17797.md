# [M] Missing validation of header name and value in codeigniter4/framework

## Summary
Severity: Medium
Advisory: GHSA-x5mq-jjr3-vmx6
CVE: CVE-2025-24013
CWE: CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-x5mq-jjr3-vmx6
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.5.8

## Details
### Impact
Lack of proper header validation for its name and value. The potential attacker can construct deliberately malformed headers with `Header` class. This could disrupt application functionality, potentially causing errors or generating invalid HTTP requests. In some cases, these malformed requests might lead to a DoS scenario if a remote service’s web application firewall interprets them as malicious and blocks further communication with the application.

### Patches
Upgrade to v4.5.8 or later.

### Workarounds
Validate HTTP header keys and/or values if using user-supplied values before passing them to `Header` class.

### Differences from CVE-2023-29197

1. **Affected Software**:
    * CVE-2023-29197 specifically addresses a vulnerability in the `guzzlehttp/psr7` library.
    * The reported issue in this Security Advisory is within the **CodeIgniter4** framework and does not depend on or use the `guzzlehttp/psr7` library.

2. **Root Cause and Implementation**:
    * The vulnerability reported arises from an issue in the **Header class** of CodeIgniter4, which is unrelated to the functionality or implementation of `guzzlehttp/psr7`.

3. **Scope of Impact**:
    * The vulnerability described in this Security Advisory affects applications built with the **CodeIgniter4** framework, which does not use or rely on the `guzzlehttp/psr7` library.

### References
* https://datatracker.ietf.org/doc/html/rfc7230#section-3.2
* https://github.com/advisories/GHSA-wxmh-65f7-jcvw

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-x5mq-jjr3-vmx6
- https://nvd.nist.gov/vuln/detail/CVE-2025-24013
- https://github.com/codeigniter4/CodeIgniter4/commit/5f8aa24280fb09947897d6b322bf1f0e038b13b6
- https://datatracker.ietf.org/doc/html/rfc7230#section-3.2
- https://github.com/advisories/GHSA-wxmh-65f7-jcvw
- https://github.com/codeigniter4/CodeIgniter4
