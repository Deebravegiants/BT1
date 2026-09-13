# [M] usb: gadget: u_serial: Add null pointer check in gserial_suspend

## Summary
Severity: Medium
Advisory: CVE-2023-53356
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53356
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: u_serial: Add null pointer check in gserial_suspend

Consider a case where gserial_disconnect has already cleared
gser->ioport. And if gserial_suspend gets called afterwards,
it will lead to accessing of gser->ioport and thus causing
null pointer dereference.

Avoid this by adding a null pointer check. Added a static
spinlock to prevent gser->ioport from becoming null after
the newly added null pointer check.

## References
- https://git.kernel.org/stable/c/2788a3553f7497075653210b42e2aeb6ba95e28e
- https://git.kernel.org/stable/c/2f6ecb89fe8feb2b60a53325b0eeb9866d88909a
- https://git.kernel.org/stable/c/374447e3367767156405bedd230c5d391f4b7962
- https://git.kernel.org/stable/c/a8ea7ed644cbf6314b5b0136b5398754b549fb8f
- https://git.kernel.org/stable/c/e60a827ac074ce6bd58305fe5a86afab5fce6a04
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53356.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53356
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
