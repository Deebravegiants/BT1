# [H] Unauthenticated DoS: avatar cache leaks goroutines when /avatar/:hash requests time out

## Summary
Severity: High
Advisory: BIT-grafana-2026-21720
Aliases: CVE-2026-21720
Ecosystem: Bitnami
Published: 2026-02-18
Source: https://osv.dev/vulnerability/BIT-grafana-2026-21720
Type: osv

## Affected
- Bitnami: `grafana` — affected >=12.3.0 <12.3.1

## Details
Every uncached /avatar/:hash request spawns a goroutine that refreshes the Gravatar image. If the refresh sits in the 10-slot worker queue longer than three seconds, the handler times out and stops listening for the result, so that goroutine blocks forever trying to send on an unbuffered channel. Sustained traffic with random hashes keeps tripping this timeout, so goroutine count grows linearly, eventually exhausting memory and causing Grafana to crash on some systems.

## References
- https://grafana.com/security/security-advisories/CVE-2026-21720
- https://nvd.nist.gov/vuln/detail/CVE-2026-21720
- https://grafana.com/security/security-advisories/cve-2026-21720
- https://access.redhat.com/security/cve/CVE-2026-21720
- https://bugzilla.redhat.com/show_bug.cgi?id=2433226
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-21720.json
