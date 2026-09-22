# [H] CVE-2022-1183

## Summary
Severity: High
Advisory: CVE-2022-1183
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-19
Source: https://osv.dev/vulnerability/CVE-2022-1183
Type: osv

## Details
On vulnerable configurations, the named daemon may, in some circumstances, terminate with an assertion failure. Vulnerable configurations are those that include a reference to http within the listen-on statements in their named.conf. TLS is used by both DNS over TLS (DoT) and DNS over HTTPS (DoH), but configurations using DoT alone are unaffected. Affects BIND 9.18.0 -> 9.18.2 and version 9.19.0 of the BIND 9.19 development branch.

## References
- https://kb.isc.org/docs/cve-2022-1183
- https://security.netapp.com/advisory/ntap-20220707-0002/
