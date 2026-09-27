# [H] undici vulnerable to TLS certificate validation bypass via dropped connect options in BalancedPool

## Summary
Severity: High
Advisory: CVE-2026-84961
Aliases: GHSA-w293-vg96-wgc3
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-84961
Type: osv

## Details
undici's BalancedPool constructor passes its entire options object through an internal deep-clone that serializes and reparses the value as JSON. Because JSON cannot represent functions, any function-valued TLS option, such as a caller-supplied checkServerIdentity callback or a custom connector inside the connect option, is silently discarded before it reaches the TLS layer. As a result a peer whose certificate the application's custom checkServerIdentity was written to reject, but which still passes Node's default hostname and chain checks, is accepted when reached through BalancedPool. The Client, Pool, and Agent dispatchers are not affected because they extract the connect and tls options before cloning. This affects undici versions from 7.24.1 up to 7.29.1 and from 8.0.0 up to 8.10.2, and only when the application supplies a function-valued connect or tls option to BalancedPool. Users should upgrade to undici 7.29.1 or 8.10.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84961.json
- https://github.com/nodejs/undici/security/advisories/GHSA-w293-vg96-wgc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-84961
