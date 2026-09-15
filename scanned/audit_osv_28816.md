# [H] usb: gadget: f_fs: Fix race between aio_cancel() and AIO request complete

## Summary
Severity: High
Advisory: CVE-2024-36894
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36894
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: f_fs: Fix race between aio_cancel() and AIO request complete

FFS based applications can utilize the aio_cancel() callback to dequeue
pending USB requests submitted to the UDC.  There is a scenario where the
FFS application issues an AIO cancel call, while the UDC is handling a
soft disconnect.  For a DWC3 based implementation, the callstack looks
like the following:

    DWC3 Gadget                               FFS Application
dwc3_gadget_soft_disconnect()              ...
  --> dwc3_stop_active_transfers()
    --> dwc3_gadget_giveback(-ESHUTDOWN)
      --> ffs_epfile_async_io_complete()   ffs_aio_cancel()
        --> usb_ep_free_request()            --> usb_ep_dequeue()

There is currently no locking implemented between the AIO completion
handler and AIO cancel, so the issue occurs if the completion routine is
running in parallel to an AIO cancel call coming from the FFS application.
As the completion call frees the USB request (io_data->req) the FFS
application is also referencing it for the usb_ep_dequeue() call.  This can
lead to accessing a stale/hanging pointer.

commit b566d38857fc ("usb: gadget: f_fs: use io_data->status consistently")
relocated the usb_ep_free_request() into ffs_epfile_async_io_complete().
However, in order to properly implement locking to mitigate this issue, the
spinlock can't be added to ffs_epfile_async_io_complete(), as
usb_ep_dequeue() (if successfully dequeuing a USB request) will call the
function driver's completion handler in the same context.  Hence, leading
into a deadlock.

Fix this issue by moving the usb_ep_free_request() back to
ffs_user_copy_worker(), and ensuring that it explicitly sets io_data->req
to NULL after freeing it within the ffs->eps_lock.  This resolves the race
condition above, as the ffs_aio_cancel() routine will not continue
attempting to dequeue a request that has already been freed, or the
ffs_user_copy_work() not freeing the USB request until the AIO cancel is
done referencing it.

This fix depends on
  commit b566d38857fc ("usb: gadget: f_fs: use io_data->status
  consistently")

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/24729b307eefcd7c476065cd7351c1a018082c19
- https://git.kernel.org/stable/c/3613e5023f09b3308545e9d1acda86017ebd418a
- https://git.kernel.org/stable/c/73c05ad46bb4fbbdb346004651576d1c8dbcffbb
- https://git.kernel.org/stable/c/9e72ef59cbe61cd1243857a6418ca92104275867
- https://git.kernel.org/stable/c/a0fdccb1c9e027e3195f947f61aa87d6d0d2ea14
- https://git.kernel.org/stable/c/d7461830823242702f5d84084bcccb25159003f4
- https://git.kernel.org/stable/c/e500b1c4e29ad0bd1c1332a1eaea2913627a92dd
- https://git.kernel.org/stable/c/f71a53148ce34898fef099b75386a3a9f4449311
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36894.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36894
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
