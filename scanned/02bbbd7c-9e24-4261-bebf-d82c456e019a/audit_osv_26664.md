# [H] net: ethernet: mvpp2_main: fix possible OOB write in mvpp2_ethtool_get_rxnfc()

## Summary
Severity: High
Advisory: CVE-2023-53495
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53495
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: mvpp2_main: fix possible OOB write in mvpp2_ethtool_get_rxnfc()

rules is allocated in ethtool_get_rxnfc and the size is determined by
rule_cnt from user space. So rule_cnt needs to be check before using
rules to avoid OOB writing or NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/349638f7e5d3c7d328565587bb7b0454bbee02e2
- https://git.kernel.org/stable/c/51fe0a470543f345e3c62b6798929de3ddcedc1d
- https://git.kernel.org/stable/c/5bb09dddc724c5f7c4dc6dd3bfebd685eecd93e8
- https://git.kernel.org/stable/c/61054a8ddb176b155a8f2bacdfefb3727187f5d9
- https://git.kernel.org/stable/c/625b70d31dd4df4b96b3ddcbe251debb33bd67f5
- https://git.kernel.org/stable/c/ba6673824efa3dc198b04a54e69dce480066d7d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53495.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53495
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
