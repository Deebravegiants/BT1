# [H] Traefik vulnerable to denial of service with Content-length header

## Summary
Severity: High
Advisory: GHSA-4vwx-54mw-vqfw
CVE: CVE-2024-28869
CWE: CWE-404, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-4vwx-54mw-vqfw
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta3 <3.0.0-rc5
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.2
- Go: `github.com/traefik/traefik` — affected >=0 <2.11.2

## Details
There is a potential vulnerability in Traefik managing requests with `Content-length` and no `body` .

Sending a `GET` request to any Traefik endpoint with the `Content-length` request header results in an indefinite hang with the default configuration. This vulnerability can be exploited by attackers to induce a denial of service.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.2
- https://github.com/traefik/traefik/releases/tag/v3.0.0-rc5

## Workarounds

For affected versions, this vulnerability can be mitigated by configuring the [readTimeout](https://doc.traefik.io/traefik/routing/entrypoints/#respondingtimeouts) option.

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-4vwx-54mw-vqfw
- https://nvd.nist.gov/vuln/detail/CVE-2024-28869
- https://github.com/traefik/traefik/commit/240b83b77351dfd8cadb91c305b84e9d22e0f9c6
- https://doc.traefik.io/traefik/routing/entrypoints/#respondingtimeouts
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.2
- https://github.com/traefik/traefik/releases/tag/v3.0.0-rc5
