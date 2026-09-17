# [M] AVideo on_publish.php Missing Authentication Check via RTMP Callback

## Summary
Severity: Medium
Advisory: CVE-2026-84187
Aliases: GHSA-v395-2xmq-cg23
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84187
Type: osv

## Details
AVideo contains a missing authentication vulnerability in plugin/Live/on_publish.php that allows unauthenticated attackers to mark arbitrary scheduled broadcasts as failed by sending crafted POST requests with schedule identifiers. Attackers can exploit the unguarded RTMP callback endpoint to modify scheduled broadcast status fields by supplying fabricated stream keys matching the pattern -ps-<N>, silently canceling any scheduled live broadcast without credentials or authorization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84187.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-v395-2xmq-cg23
- https://nvd.nist.gov/vuln/detail/CVE-2026-84187
- https://www.vulncheck.com/advisories/avideo-on-publish-php-missing-authentication-check-via-rtmp-callback
