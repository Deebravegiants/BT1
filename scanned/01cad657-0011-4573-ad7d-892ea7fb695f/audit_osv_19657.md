# [H] CVE-2021-23270

## Summary
Severity: High
Advisory: CVE-2021-23270
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-12
Source: https://osv.dev/vulnerability/CVE-2021-23270
Type: osv

## Details
In Gargoyle OS 1.12.0, when IPv6 is used, a routing loop can occur that generates excessive network traffic between an affected device and its upstream ISP's router. This occurs when a link prefix route points to a point-to-point link, a destination IPv6 address belongs to the prefix and is not a local IPv6 address, and a router advertisement is received with at least one global unique IPv6 prefix for which the on-link flag is set.

## References
- https://github.com/ericpaulbishop/gargoyle/commit/24afe944a6ffff53d84a748384e276a4e95912ec
