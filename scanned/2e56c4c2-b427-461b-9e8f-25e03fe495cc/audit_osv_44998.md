# [H] exposing HTTP/3 early data

## Summary
Severity: High
Advisory: CVE-2026-9545
Aliases: CURL-CVE-2026-9545
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-9545
Type: osv

## Details
In this scenario, libcurl first uses a proper HTTP/3 server for the initial
transfers, and when it makes a second transfer to the same site it has been
replaced by the attacker's impostor machine - without a valid certificate.

When libcurl returns to the hostname the second time with a cached SSL session
(`CURLOPT_SSL_SESSIONID_CACHE` is not disabled) and early data enabled (the
`CURLSSLOPT_EARLYDATA` bit is set in `CURLOPT_SSL_OPTIONS`), libcurl might
send off the second request's bytes on that new connection *before* enforcing
the certificate verification failure. Potentially leaking sensitive
information.

## References
- https://curl.se/docs/CVE-2026-9545.html
- https://curl.se/docs/CVE-2026-9545.json
- https://hackerone.com/reports/3752888
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9545.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9545
