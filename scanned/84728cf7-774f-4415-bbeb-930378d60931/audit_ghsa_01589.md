# [M] Cross-site scripting (XSS) vulnerability in the fallback authentication endpoint

## Summary
Severity: Medium
Advisory: GHSA-3x8c-fmpc-5rmq
CVE: CVE-2020-26891
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-10-16
Source: https://github.com/advisories/GHSA-3x8c-fmpc-5rmq
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.21.0

## Details
### Impact
The fallback authentication endpoint served via Synapse was vulnerable to cross-site scripting (XSS) attacks. The impact depends on the configuration of the domain that Synapse is deployed on, but may allow access to cookies and other browser data, CSRF vulnerabilities, and access to other resources served on the same domain or parent domains.

### Patches
This is fixed by #8444, which is included in Synapse v1.21.0.

### Workarounds
If the homeserver is not configured to use reCAPTCHA, consent (terms of service), or single sign-on then the affected endpoint can be blocked at a reverse proxy:

* `/_matrix/client/r0/auth/.*/fallback/web`
* `/_matrix/client/unstable/auth/.*/fallback/web`

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-3x8c-fmpc-5rmq
- https://nvd.nist.gov/vuln/detail/CVE-2020-26891
- https://github.com/matrix-org/synapse/pull/8444
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases
- https://github.com/matrix-org/synapse/releases/tag/v1.21.2
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2020-238.yaml
- https://matrix.org/blog/2020/10/15/synapse-1-21-2-released-and-security-advisory
