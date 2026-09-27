# [H] RDMA/srpt: Do not register event handler until srpt device is fully setup

## Summary
Severity: High
Advisory: CVE-2024-26872
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26872
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/srpt: Do not register event handler until srpt device is fully setup

Upon rare occasions, KASAN reports a use-after-free Write
in srpt_refresh_port().

This seems to be because an event handler is registered before the
srpt device is fully setup and a race condition upon error may leave a
partially setup event handler in place.

Instead, only register the event handler after srpt device initialization
is complete.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/6413e78086caf7bf15639923740da0d91fdfd090
- https://git.kernel.org/stable/c/7104a00fa37ae898a827381f1161fa3286c8b346
- https://git.kernel.org/stable/c/85570b91e4820a0db9d9432098778cafafa7d217
- https://git.kernel.org/stable/c/bdd895e0190c464f54f84579e7535d80276f0fc5
- https://git.kernel.org/stable/c/c21a8870c98611e8f892511825c9607f1e2cd456
- https://git.kernel.org/stable/c/e362d007294955a4fb929e1c8978154a64efdcb6
- https://git.kernel.org/stable/c/ec77fa12da41260c6bf9e060b89234b980c5130f
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26872.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
