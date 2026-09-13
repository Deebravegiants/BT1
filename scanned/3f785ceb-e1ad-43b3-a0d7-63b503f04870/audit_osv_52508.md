# [M] CVE-2021-47523

## Summary
Severity: Medium
Advisory: CVE-2021-47523
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47523
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/hfi1: Fix leak of rcvhdrtail_dummy_kvaddr

This buffer is currently allocated in hfi1_init():

	if (reinit)
		ret = init_after_reset(dd);
	else
		ret = loadtime_init(dd);
	if (ret)
		goto done;

	/* allocate dummy tail memory for all receive contexts */
	dd->rcvhdrtail_dummy_kvaddr = dma_alloc_coherent(&dd->pcidev->dev,
							 sizeof(u64),
							 &dd->rcvhdrtail_dummy_dma,
							 GFP_KERNEL);

	if (!dd->rcvhdrtail_dummy_kvaddr) {
		dd_dev_err(dd, "cannot allocate dummy tail memory\n");
		ret = -ENOMEM;
		goto done;
	}

The reinit triggered path will overwrite the old allocation and leak it.

Fix by moving the allocation to hfi1_alloc_devdata() and the deallocation
to hfi1_free_devdata().

## References
- https://git.kernel.org/stable/c/2c08271f4ed0e24633b3f81ceff61052b9d45efc
- https://git.kernel.org/stable/c/60a8b5a1611b4a26de4839ab9c1fc2a9cf3e17c1
- https://git.kernel.org/stable/c/834d0fb978643eaf09da425de197cc16a7c2761b
