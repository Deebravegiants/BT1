# [M] Traefik vulnerable to potential DDoS via ACME HTTPChallenge

## Summary
Severity: Medium
Advisory: GHSA-8g85-whqh-cr2f
CVE: CVE-2023-47124
CWE: CWE-400, CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-8g85-whqh-cr2f
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.10.6
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.0.0-beta5

## Details
## Impact

There is a potential vulnerability in Traefik managing the ACME HTTP challenge.

When Traefik is configured to use the [HTTPChallenge](https://doc.traefik.io/traefik/https/acme/#httpchallenge) to generate and renew the Let's Encrypt TLS certificates, the delay authorized to solve the challenge (50 seconds) can be exploited by attackers ([slowloris attack](https://www.cloudflare.com/learning/ddos/ddos-attack-tools/slowloris/)).
 
## Patches

- https://github.com/traefik/traefik/releases/tag/v2.10.6
- https://github.com/traefik/traefik/releases/tag/v3.0.0-beta5

## Workarounds

Replace the HTTPChallenge with the [TLSChallenge](https://doc.traefik.io/traefik/https/acme/#tlschallenge) or the [DNSChallenge](https://doc.traefik.io/traefik/https/acme/#dnschallenge).

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-8g85-whqh-cr2f
- https://nvd.nist.gov/vuln/detail/CVE-2023-47124
- https://doc.traefik.io/traefik/https/acme/#dnschallenge
- https://doc.traefik.io/traefik/https/acme/#httpchallenge
- https://doc.traefik.io/traefik/https/acme/#tlschallenge
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.10.6
- https://github.com/traefik/traefik/releases/tag/v3.0.0-beta5
- https://www.cloudflare.com/learning/ddos/ddos-attack-tools/slowloris
