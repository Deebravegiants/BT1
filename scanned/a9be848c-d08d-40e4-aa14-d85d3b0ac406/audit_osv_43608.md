# [H] s390/qeth: Check CAP_NET_ADMIN for private ioctls

## Summary
Severity: High
Advisory: CVE-2026-74467
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74467
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/qeth: Check CAP_NET_ADMIN for private ioctls

Gate the SIOCDEVPRIVATE ioctl commands SIOC_QETH_ADP_SET_SNMP_CONTROL,
SIOC_QETH_GET_CARD_TYPE and SIOC_QETH_QUERY_OAT with CAP_NET_ADMIN
capable check to ensure unprivileged users cannot invoke them.

## References
- https://git.kernel.org/stable/c/3ea5210db058347481c93849786982f874f7be2d
- https://git.kernel.org/stable/c/4e48168825818bf4a13c743582227d15f1d30d04
- https://git.kernel.org/stable/c/8fb69547924bbb3d7c900a0d7d137a7234db3f5f
- https://git.kernel.org/stable/c/93a0a846ec59a88e0c402878a15357a5ce430eb4
- https://git.kernel.org/stable/c/b40c74262f7e1e601221cebccdbdb2b392ff9976
- https://git.kernel.org/stable/c/bd63c7879eaa87f1958f7ee027813356fcd9ff11
- https://git.kernel.org/stable/c/d211028bac1bd0fff0026bfa2a8328e5b78cd0e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74467.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74467
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
