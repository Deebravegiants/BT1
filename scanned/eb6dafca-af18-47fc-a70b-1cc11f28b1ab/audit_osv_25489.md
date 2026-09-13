# [M] Out-of-bounds read when processing a received IPv6 packet

## Summary
Severity: Medium
Advisory: CVE-2023-37459
Aliases: GHSA-6648-m23r-hq8c
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-09-15
Source: https://osv.dev/vulnerability/CVE-2023-37459
Type: osv

## Details
Contiki-NG is an operating system for internet-of-things devices. In versions 4.9 and prior, when a packet is received, the Contiki-NG network stack attempts to start the periodic TCP timer if it is a TCP packet with the SYN flag set. But the implementation does not first verify that a full TCP header has been received. Specifically, the implementation attempts to access the flags field from the TCP buffer in the following conditional expression in the `check_for_tcp_syn` function. For this reason, an attacker can inject a truncated TCP packet, which will lead to an out-of-bound read from the packet buffer. As of time of publication, a patched version is not available. As a workaround, one can apply the changes in Contiki-NG pull request #2510 to patch the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37459.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-6648-m23r-hq8c
- https://nvd.nist.gov/vuln/detail/CVE-2023-37459
- https://github.com/contiki-ng/contiki-ng/pull/2510
