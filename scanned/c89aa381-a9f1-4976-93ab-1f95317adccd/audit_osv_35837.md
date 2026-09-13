# [C] SCTP needs to better-check INIT ACK chunk parameters

## Summary
Severity: Critical
Advisory: CVE-2026-15422
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:U/S:P/AU:Y/R:U/V:C/RE:H/U:Red)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-15422
Type: osv

## Details
The illumos SCTP inbound path performs association lookup for INIT ACK chunks without adequately validating the address parameters carried in the chunk. Since this lookup runs during packet classification (i.e. before SCTP integrity checks or IPsec policy are applied) a remote, unauthenticated attacker can send a crafted SCTP INIT ACK packet with malformed address parameters to cause an out-of-bounds access and kernel heap corruption, which may lead to remote code execution. The flaw has existed since 2010 (illumos-gate commit a5407c02), and affects any illumos distribution prior to illumos-gate commit 53a3efde.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15422.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15422
- https://illumos.org/issues/18117
- https://github.com/illumos/illumos-gate/commit/53a3efdeff8e6745bbfb69c5360f94962fb79e75
- https://github.com/illumos/illumos-gate
- https://illumos.topicbox.com/groups/developer/Ta1a8e2e1f7f928df/18117-sctp-needs-to-better-check-init-ack-chunk-parameters
