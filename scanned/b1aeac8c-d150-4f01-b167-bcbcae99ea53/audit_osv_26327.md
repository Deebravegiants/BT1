# [M] usb: dwc2: fix possible NULL pointer dereference caused by driver concurrency

## Summary
Severity: Medium
Advisory: CVE-2023-52855
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52855
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.14.330, >=4.15.0 <4.19.299, >=4.20.0 <5.4.261, >=5.5.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc2: fix possible NULL pointer dereference caused by driver concurrency

In _dwc2_hcd_urb_enqueue(), "urb->hcpriv = NULL" is executed without
holding the lock "hsotg->lock". In _dwc2_hcd_urb_dequeue():

    spin_lock_irqsave(&hsotg->lock, flags);
    ...
	if (!urb->hcpriv) {
		dev_dbg(hsotg->dev, "## urb->hcpriv is NULL ##\n");
		goto out;
	}
    rc = dwc2_hcd_urb_dequeue(hsotg, urb->hcpriv); // Use urb->hcpriv
    ...
out:
    spin_unlock_irqrestore(&hsotg->lock, flags);

When _dwc2_hcd_urb_enqueue() and _dwc2_hcd_urb_dequeue() are
concurrently executed, the NULL check of "urb->hcpriv" can be executed
before "urb->hcpriv = NULL". After urb->hcpriv is NULL, it can be used
in the function call to dwc2_hcd_urb_dequeue(), which can cause a NULL
pointer dereference.

This possible bug is found by an experimental static analysis tool
developed by myself. This tool analyzes the locking APIs to extract
function pairs that can be concurrently executed, and then analyzes the
instructions in the paired functions to identify possible concurrency
bugs including data races and atomicity violations. The above possible
bug is reported, when my tool analyzes the source code of Linux 6.5.

To fix this possible bug, "urb->hcpriv = NULL" should be executed with
holding the lock "hsotg->lock". After using this patch, my tool never
reports the possible bug, with the kernelconfiguration allyesconfig for
x86_64. Because I have no associated hardware, I cannot test the patch
in runtime testing, and just verify it according to the code logic.

## References
- https://git.kernel.org/stable/c/14c9ec34e8118fbffd7f5431814d767726323e72
- https://git.kernel.org/stable/c/3e851a77a13ce944d703721793f49ee82622986d
- https://git.kernel.org/stable/c/64c47749fc7507ed732e155c958253968c1d275e
- https://git.kernel.org/stable/c/6b21a22728852d020a6658d39cd7bb7e14b07790
- https://git.kernel.org/stable/c/a7bee9598afb38004841a41dd8fe68c1faff4e90
- https://git.kernel.org/stable/c/bdb3dd4096302d6b87441fdc528439f171b04be6
- https://git.kernel.org/stable/c/ef307bc6ef04e8c1ea843231db58e3afaafa9fa6
- https://git.kernel.org/stable/c/fcaafb574fc88a52dce817f039f7ff2f9da38001
- https://git.kernel.org/stable/c/fed492aa6493a91a77ebd51da6fb939c98d94a0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52855.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52855
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
