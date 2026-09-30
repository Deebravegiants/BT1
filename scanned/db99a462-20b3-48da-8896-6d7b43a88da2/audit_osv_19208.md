# [H] CVE-2020-8659

## Summary
Severity: High
Advisory: CVE-2020-8659
Aliases: GHSA-jwcm-4pwp-c2qv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-04
Source: https://osv.dev/vulnerability/CVE-2020-8659
Type: osv

## Details
CNCF Envoy through 1.13.0 may consume excessive amounts of memory when proxying HTTP/1.1 requests or responses with many small (i.e. 1 byte) chunks.

## References
- https://access.redhat.com/errata/RHSA-2020:0734
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-jwcm-4pwp-c2qv
- https://lists.debian.org/debian-lts-announce/2022/05/msg00025.html
- https://www.envoyproxy.io/docs/envoy/v1.13.1/intro/version_history
