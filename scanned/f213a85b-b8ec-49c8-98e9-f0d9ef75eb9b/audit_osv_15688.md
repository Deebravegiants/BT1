# [C] CVE-2019-18801

## Summary
Severity: Critical
Advisory: CVE-2019-18801
Aliases: GHSA-gxvv-x4p2-rppp
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-13
Source: https://osv.dev/vulnerability/CVE-2019-18801
Type: osv

## Details
An issue was discovered in Envoy 1.12.0. An untrusted remote client may send HTTP/2 requests that write to the heap outside of the request buffers when the upstream is HTTP/1. This may be used to corrupt nearby heap contents (leading to a query-of-death scenario) or may be used to bypass Envoy's access control mechanisms such as path based routing. An attacker can also modify requests from other users that happen to be proximal temporally and spatially.

## References
- https://groups.google.com/forum/#%21forum/envoy-users
- https://access.redhat.com/errata/RHSA-2019:4222
- https://github.com/envoyproxy/envoy/commits/master
- https://blog.envoyproxy.io
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-gxvv-x4p2-rppp
