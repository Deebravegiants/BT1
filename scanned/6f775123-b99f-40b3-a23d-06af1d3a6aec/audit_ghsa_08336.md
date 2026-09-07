# [M] Neotoma: Unauthenticated Inspector/API access via reverse-proxy loopback auth bypass

## Summary
Severity: Medium
Advisory: GHSA-5cvp-p7p4-mcx9
CVE: CVE-2026-45577
CWE: CWE-288, CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-5cvp-p7p4-mcx9
Type: github-advisory

## Affected
- npm: `neotoma` — affected >=0.6.0 <0.11.1

## Details
Neotoma versions starting at v0.6.0 can treat public reverse-proxied requests as local when the app receives them over a loopback socket and no Bearer token is present.

In affected deployments, the REST auth middleware can resolve unauthenticated requests as the local development user, making the hosted Inspector and related API surface reachable without credentials.

Impact: unauthorized access to production data exposed through the Inspector/API on affected deployments.

Affected condition: a public deployment behind a reverse proxy or same-host tunnel that forwards traffic to the Node process over loopback.

Remediation implemented on the main branch: local-request detection now fails closed in production unless loopback trust is explicitly enabled, and forwarded public clients remain remote.

Patched release version is pending; this draft will be updated once the fix is released.

## References
- https://github.com/markmhendrickson/neotoma/security/advisories/GHSA-5cvp-p7p4-mcx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45577
- https://github.com/markmhendrickson/neotoma
- https://github.com/markmhendrickson/neotoma/releases/tag/v0.11.1
