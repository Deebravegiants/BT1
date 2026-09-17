# [H] netfilter: conntrack_irc: fix possible out-of-bounds read

## Summary
Severity: High
Advisory: CVE-2026-53268
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53268
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack_irc: fix possible out-of-bounds read

When parsing fails after we've matched the command string we
should bail out instead of trying to match a different command.

This helper should be deprecated, given prevalence of TLS I doubt it has
any relevance in 2026.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0afc802160af0df61ed374fdb97fb34cfe5cdf2f
- https://git.kernel.org/stable/c/4cdda7f868f48e2f81579371584fdbdce37df2c8
- https://git.kernel.org/stable/c/573810f61bcd6b6815e2ff53bbdd2b9c9d747176
- https://git.kernel.org/stable/c/66eba0ffce3b7e11449946b4cbbef8ea36112f56
- https://git.kernel.org/stable/c/7c34f91305292083253df6a9f6c8ede02d4ccaea
- https://git.kernel.org/stable/c/8a1d6e40dedfe1068aee094d851bd69e289c9fd6
- https://git.kernel.org/stable/c/9e5da2379f968a3ea5a6e38921ab6201576466dc
- https://git.kernel.org/stable/c/ddddd8271359961e403d11c90c9ba9fc38914f7e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53268.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53268
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
