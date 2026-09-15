# [C] netfilter: flowtable: use dst in this direction when pushing IPIP header

## Summary
Severity: Critical
Advisory: CVE-2026-72249
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72249
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: use dst in this direction when pushing IPIP header

When pushing the IPIP header, the route of the other direction is used
to calculate the headroom, use the route in this direction. Accessing
the other tuple to set the IP source and destination is fine because
this tuple does not provide such information to avoid storing redundant
information. However, this tuple already provides the dst for this
direction, this went unnoticed because this bug affects headroom and
iph->frag_off only at this stage.

## References
- https://git.kernel.org/stable/c/c328b90c17fc5fa7786503695152880b2afb9326
- https://git.kernel.org/stable/c/ecb78fbb03d3f86e2e93767875e273308086a424
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72249.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72249
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
