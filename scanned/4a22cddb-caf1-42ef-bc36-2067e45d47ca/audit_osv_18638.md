# [M] CVE-2020-29362

## Summary
Severity: Medium
Advisory: CVE-2020-29362
Aliases: GHSA-5wpq-43j2-6qwc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-12-16
Source: https://osv.dev/vulnerability/CVE-2020-29362
Type: osv

## Details
An issue was discovered in p11-kit 0.21.1 through 0.23.21. A heap-based buffer over-read has been discovered in the RPC protocol used by thep11-kit server/remote commands and the client library. When the remote entity supplies a byte array through a serialized PKCS#11 function call, the receiving entity may allow the reading of up to 4 bytes of memory past the heap allocation.

## References
- https://github.com/p11-glue/p11-kit/releases
- https://github.com/p11-glue/p11-kit/security/advisories/GHSA-5wpq-43j2-6qwc
- https://lists.debian.org/debian-lts-announce/2021/01/msg00002.html
- https://www.debian.org/security/2021/dsa-4822
