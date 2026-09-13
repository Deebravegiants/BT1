# [H] i2c: core: fix adapter registration race

## Summary
Severity: High
Advisory: CVE-2026-53400
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53400
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: core: fix adapter registration race

Adapters can be looked up based on their id using i2c_get_adapter()
which takes a reference to the embedded struct device.

Make sure that the adapter (including its struct device) has been
initialised before adding it to the IDR to avoid accessing uninitialised
data which could, for example, lead to NULL-pointer dereferences or
use-after-free.

Note that the i2c-dev chardev, which is registered from a bus notifier,
currently uses i2c_get_adapter() so the adapter needs to be added to the
IDR before registration.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1febb174815bcae56d73587e99e8f87e02f0784d
- https://git.kernel.org/stable/c/2e57c788e71f1763445f812eba4e0b4a2fbd0646
- https://git.kernel.org/stable/c/6a946038f2a5a8c29048c6af369d4e391448a5c5
- https://git.kernel.org/stable/c/78793c75dc6d0ff2e4d50ad617349b328a99054e
- https://git.kernel.org/stable/c/a4365bc41baaf67f3a5aa8556d23544e6ec7480a
- https://git.kernel.org/stable/c/a4c8094bbf4c6fa68b17e3b16f6a0a1b7a14f3e0
- https://git.kernel.org/stable/c/ba14d7cf2fe7284610a29854bdff22b2537d3ce6
- https://git.kernel.org/stable/c/da9d8d9711f78deebc202d0cffcf577e45ee8621
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53400.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53400
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
