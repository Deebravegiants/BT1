# [H] Bluetooth: qca: fix info leak when fetching fw build id

## Summary
Severity: High
Advisory: CVE-2024-36032
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36032
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.162, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: qca: fix info leak when fetching fw build id

Add the missing sanity checks and move the 255-byte build-id buffer off
the stack to avoid leaking stack data through debugfs in case the
build-info reply is malformed.

## References
- https://git.kernel.org/stable/c/57062aa13e87b1a78a4a8f6cb5fab6ba24f5f488
- https://git.kernel.org/stable/c/62d5550ab62042dcceaf18844d0feadbb962cffe
- https://git.kernel.org/stable/c/6b63e0ef4d3ce0080395e5091fba2023f246c45a
- https://git.kernel.org/stable/c/a571044cc0a0c944e7c12237b6768aeedd7480e1
- https://git.kernel.org/stable/c/cda0d6a198e2a7ec6f176c36173a57bdd8af7af2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36032.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36032
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
