# [C] sealed-env: TOTP secret embedded in unseal token payload (enterprise mode)

## Summary
Severity: Critical
Advisory: GHSA-x3r2-fj3r-g5mv
CVE: CVE-2026-45091
CWE: CWE-200, CWE-522
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-x3r2-fj3r-g5mv
Type: github-advisory

## Affected
- npm: `sealed-env` — affected >=0 <0.1.0-alpha.4
- Maven: `io.github.davidalmeidac:sealed-env-core` — affected >=0 <0.1.0-alpha.4

## Details
In sealed-env enterprise mode, versions 0.1.0-alpha.1 through 0.1.0-alpha.3 embedded the operator's literal TOTP secret in the JWS payload of every minted unseal token. JWS payload is base64-encoded JSON, NOT encrypted. Any party who could observe a minted token (CI build logs, container env dumps, kubectl describe pod, Sentry/Rollbar stack traces, log aggregators) could decode the payload and extract the TOTP secret in plaintext.

An attacker with (a) the master key (e.g. from a separate compromise such as a leaked CI secret) and (b) any single leaked unseal token can use the extracted TOTP secret to mint new valid unseal tokens for any future deploy indefinitely, breaking the second-factor property the library claimed.

Patched in 0.1.0-alpha.4 by replacing the embedded secret with a salt-bound HMAC derivative (`enterprise_epoch = HMAC(totpSecret, salt || "epoch-v1")`). The TOTP secret never leaves the operator's machine in the new design. The wire format change is incompatible — files sealed by affected versions must be re-sealed and the TOTP secret rotated. Full migration playbook in CHANGELOG.md.

Reported by an external reviewer who decoded the payload of a real minted token and confirmed bit-for-bit equality with the operator's .env.local TOTP secret.

## References
- https://github.com/davidalmeidac/sealed-env/security/advisories/GHSA-x3r2-fj3r-g5mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-45091
- https://github.com/davidalmeidac/sealed-env
