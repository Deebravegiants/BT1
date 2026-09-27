# [H] net/sched: taprio: always validate TCA_TAPRIO_ATTR_PRIOMAP

## Summary
Severity: High
Advisory: CVE-2024-36974
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-18
Source: https://osv.dev/vulnerability/CVE-2024-36974
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: taprio: always validate TCA_TAPRIO_ATTR_PRIOMAP

If one TCA_TAPRIO_ATTR_PRIOMAP attribute has been provided,
taprio_parse_mqprio_opt() must validate it, or userspace
can inject arbitrary data to the kernel, the second time
taprio_change() is called.

First call (with valid attributes) sets dev->num_tc
to a non zero value.

Second call (with arbitrary mqprio attributes)
returns early from taprio_parse_mqprio_opt()
and bad things can happen.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/0bf6cc96612bd396048f57d63f1ad454a846e39c
- https://git.kernel.org/stable/c/6db4af09987cc5d5f0136bd46148b0e0460dae5b
- https://git.kernel.org/stable/c/724050ae4b76e4fae05a923cb54101d792cf4404
- https://git.kernel.org/stable/c/c37a27a35eadb59286c9092c49c241270c802ae2
- https://git.kernel.org/stable/c/c6041e7124464ce7e896ee3f912897ce88a0c4ec
- https://git.kernel.org/stable/c/d3dde4c217f0c31ab0621912e682b57e677dd923
- https://git.kernel.org/stable/c/f921a58ae20852d188f70842431ce6519c4fdc36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36974.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36974
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
