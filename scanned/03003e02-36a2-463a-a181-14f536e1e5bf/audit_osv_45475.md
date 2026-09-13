# [M] When asked to both use a `.netrc` file for credentials and to follow HTTP redirects, libcurl...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1208
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1208
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.20.0+0

## Details
When asked to both use a `.netrc` file for credentials and to follow HTTP
redirects, libcurl could leak the password used for the first host to the
followed-to host under certain circumstances.

## References
- https://curl.se/docs/CVE-2026-6429.html
- https://curl.se/docs/CVE-2026-6429.json
- https://github.com/advisories/GHSA-2pvc-5qw9-h3ph
- https://hackerone.com/reports/3677759
- https://nvd.nist.gov/vuln/detail/CVE-2026-6429
