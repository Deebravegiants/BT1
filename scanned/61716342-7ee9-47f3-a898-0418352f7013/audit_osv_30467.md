# [M] mctp i2c: handle NULL header address

## Summary
Severity: Medium
Advisory: CVE-2024-53043
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53043
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mctp i2c: handle NULL header address

daddr can be NULL if there is no neighbour table entry present,
in that case the tx packet should be dropped.

saddr will usually be set by MCTP core, but check for NULL in case a
packet is transmitted by a different protocol.

## References
- https://git.kernel.org/stable/c/01e215975fd80af81b5b79f009d49ddd35976c13
- https://git.kernel.org/stable/c/4707893315802a0917231b94cb20cbe50ccbfe03
- https://git.kernel.org/stable/c/8c222adadc1612e4f097688875962a28e3f5ab44
- https://git.kernel.org/stable/c/8e886e44397ba89f6e8da8471386112b4f5b67b7
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53043.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
