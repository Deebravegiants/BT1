# [H] CVE-2019-15225

## Summary
Severity: High
Advisory: CVE-2019-15225
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15225
Type: osv

## Details
In Envoy through 1.11.1, users may configure a route to match incoming path headers via the libstdc++ regular expression implementation. A remote attacker may send a request with a very long URI to result in a denial of service (memory consumption). This is a related issue to CVE-2019-14993.

## References
- https://github.com/envoyproxy/envoy/issues/7728
