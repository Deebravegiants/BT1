# [H] In this scenario, libcurl first uses a proper HTTP/3 server for the initial transfers, and when...

## Summary
Severity: High
Advisory: JLSEC-2026-1220
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1220
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.11.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.11.0+0 <8.21.0+0

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
- https://github.com/advisories/GHSA-6v72-wfcj-jv53
- https://hackerone.com/reports/3752888
- https://nvd.nist.gov/vuln/detail/CVE-2026-9545
