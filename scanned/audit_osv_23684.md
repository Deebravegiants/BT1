# [M] nfc: st21nfca: fix memory leaks in EVT_TRANSACTION handling

## Summary
Severity: Medium
Advisory: CVE-2022-49331
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49331
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: st21nfca: fix memory leaks in EVT_TRANSACTION handling

Error paths do not free previously allocated memory. Add devm_kfree() to
those failure paths.

## References
- https://git.kernel.org/stable/c/3eca2c42daa4659965db6817479027cbc6df7899
- https://git.kernel.org/stable/c/54423649bc0ed464b75807a7cf2857a5871f738f
- https://git.kernel.org/stable/c/55904086041ba4ee4070187b36590f8f8d6df4cd
- https://git.kernel.org/stable/c/593773088d615a46a42c97e01a0550d192bb7f74
- https://git.kernel.org/stable/c/6fce324b530dd74750ad870699e33eeed1029ded
- https://git.kernel.org/stable/c/996419e0594abb311fb958553809f24f38e7abbe
- https://git.kernel.org/stable/c/d221ce54ce331c1a23be71eebf57f6a088632383
- https://git.kernel.org/stable/c/db836b97464d44340b568e041fd24602858713f7
- https://git.kernel.org/stable/c/f444ecd3f57f4ba5090fe8b6756933e37de4226e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49331.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49331
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
