# [H] gve: Account for stopped queues when reading NIC stats

## Summary
Severity: High
Advisory: CVE-2024-42162
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42162
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

gve: Account for stopped queues when reading NIC stats

We now account for the fact that the NIC might send us stats for a
subset of queues. Without this change, gve_get_ethtool_stats might make
an invalid access on the priv->stats_report->stats array.

## References
- https://git.kernel.org/stable/c/32675d828c8a392e20d5b42375ed112c407e4b62
- https://git.kernel.org/stable/c/af9bcf910b1f86244f39e15e701b2dc564b469a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42162.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42162
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
