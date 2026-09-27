# [M] Mautic Focus component Vulnerable to SSRF

## Summary
Severity: Medium
Advisory: GHSA-jmv8-8j9j-rcpc
CVE: CVE-2026-9557
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-jmv8-8j9j-rcpc
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=4.0.0
- Packagist: `mautic/core` — affected >=5.0.0 <5.2.11
- Packagist: `mautic/core` — affected >=6.0.0 <6.0.9
- Packagist: `mautic/core` — affected >=7.0.0 <7.1.2

## Details
### Summary
A Server-Side Request Forgery (SSRF) vulnerability exists in the Mautic Focus component (`MauticFocusBundle`). Under certain conditions, insufficiency in validating user-supplied URLs allows authenticated users to trigger outbound HTTP requests from the hosting server.

### Impact
An authenticated user with access to the Mautic panel can exploit this vulnerability to perform internal port probing or force the server to initiate requests to external or arbitrary internal destinations. This can enable internal network reconnaissance or mapping of firewalled infrastructure.

### Patched Versions
This security issue has been fixed in the following releases:
* **7.1.2**
* **6.0.9**
* **5.2.11**
* **4.4.20** [ELTS](https://mautic.org/extended-long-term-support-elts/)

Mautic strongly recommend upgrading to the latest version corresponding to your release branch.

### Workarounds
There are no official workarounds. To completely mitigate the exposure without upgrading, disabling or limiting external network access from the Mautic web server to internal-only subnets/local hosts is recommended.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-jmv8-8j9j-rcpc
- https://nvd.nist.gov/vuln/detail/CVE-2026-9557
- https://github.com/mautic/mautic
