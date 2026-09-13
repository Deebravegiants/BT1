# [C] SSOReady has an XML Signature Bypass via differential XML parsing

## Summary
Severity: Critical
Advisory: GHSA-j2hr-q93x-gxvh
CVE: CVE-2024-47832
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-11
Source: https://github.com/advisories/GHSA-j2hr-q93x-gxvh
Type: github-advisory

## Affected
- Go: `github.com/ssoready/ssoready` — affected >=0 <0.0.0-20241009153838-7f92a0630439

## Details
Affected versions are vulnerable to XML signature bypass attacks. An attacker can carry out signature bypass if you have access to certain IDP-signed messages. The underlying mechanism exploits differential behavior between XML parsers.

Users of https://ssoready.com, the public hosted instance of SSOReady, are unaffected. We advise folks who self-host SSOReady to upgrade to 7f92a06 or later. Do so by updating your SSOReady Docker images from `sha-...` to `sha-7f92a06`. The documentation for self-hosting SSOReady is available [here](https://ssoready.com/docs/self-hosting/self-hosting-sso-ready).

Vulnerability was discovered by @ahacker1-securesaml. It's likely the precise mechanism of attack affects other SAML implementations, so the reporter and I (@ucarion) have agreed to not disclose it in detail publicly at this time.

## References
- https://github.com/ssoready/ssoready/security/advisories/GHSA-j2hr-q93x-gxvh
- https://nvd.nist.gov/vuln/detail/CVE-2024-47832
- https://github.com/ssoready/ssoready/commit/7f92a0630439972fcbefa8c7eafe8c144bd89915
- https://github.com/ssoready/ssoready
- https://pkg.go.dev/vuln/GO-2024-3185
- https://ssoready.com/docs/self-hosting/self-hosting-sso-ready
