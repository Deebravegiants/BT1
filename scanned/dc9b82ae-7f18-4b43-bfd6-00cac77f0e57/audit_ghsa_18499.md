# [H] private-ip vulnerable to Server-Side Request Forgery

## Summary
Severity: High
Advisory: GHSA-9h3q-32c7-r533
CVE: CVE-2025-8020
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-07-23
Source: https://github.com/advisories/GHSA-9h3q-32c7-r533
Type: github-advisory

## Affected
- npm: `private-ip` — affected >=0

## Details
All versions of the package private-ip are vulnerable to Server-Side Request Forgery (SSRF), where an attacker can provide an IP or hostname that resolves to a multicast IP address (224.0.0.0/4) which is not included as part of the private IP ranges in the package's source code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8020
- https://gist.github.com/lirantal/ed18a4493ca9fe4429957c79454a9df1
- https://github.com/frenchbread/private-ip
- https://security.snyk.io/vuln/SNYK-JS-PRIVATEIP-9510757
