# [C] Appsmith: Caddy admin API exposed without authentication

## Summary
Severity: Critical
Advisory: BIT-appsmith-2026-55454
Aliases: CVE-2026-55454, GHSA-8jvv-gwqg-6vjc
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-appsmith-2026-55454
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <2.1.0

## Details
Appsmith is a platform to build admin panels, internal tools, and dashboards. Prior to 2.1, the bundled Caddy reverse-proxy's admin API — which has no authentication by default — is bound on 0.0.0.0:2019 inside the container. While this listener is not directly published to the host by docker-compose.yml, it is reachable from the Appsmith server process itself or a SSRF vulnerability. An authenticated low-privileged user can therefore drive the SSRF to issue POST /load (or any other admin-API call) against http://0.0.0.0:2019/, fully replacing the live Caddy configuration and taking over the reverse proxy. This vulnerability is fixed in 2.1.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-8jvv-gwqg-6vjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-55454
