# [C] authentik has Insufficient Session verification for Remote Access Control endpoint access

## Summary
Severity: Critical
Advisory: BIT-authentik-2025-52553
Aliases: CVE-2025-52553, GHSA-wr3v-9p2c-chx7
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2025-52553
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2025.6.0 <2025.6.3

## Details
authentik is an open-source identity provider. After authorizing access to a RAC endpoint, authentik creates a token which is used for a single connection and is sent to the client in the URL. This token is intended to only be valid for the session of the user who authorized the connection, however this check is missing in versions prior to 2025.6.3 and 2025.4.3. When, for example, using RAC during a screenshare, a malicious user could access the same session by copying the URL from the shown browser. authentik 2025.4.3 and 2025.6.3 fix this issue. As a workaround, it is recommended to decrease the duration a token is valid for (in the RAC Provider settings, set Connection expiry to `minutes=5` for example). The maintainers of authentik also recommend enabling the option Delete authorization on disconnect.

## References
- https://github.com/goauthentik/authentik/commit/0e07414e9739b318cff9401a413a5fe849545325
- https://github.com/goauthentik/authentik/commit/65373ab21711d58147b5cb9276c5b5876baaa5eb
- https://github.com/goauthentik/authentik/commit/7100d3c6741853f1cfe3ea2073ba01823ab55caa
- https://github.com/goauthentik/authentik/security/advisories/GHSA-wr3v-9p2c-chx7
- https://nvd.nist.gov/vuln/detail/CVE-2025-52553
