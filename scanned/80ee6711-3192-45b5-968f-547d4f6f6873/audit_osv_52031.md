# [M] CVE-2021-46986

## Summary
Severity: Medium
Advisory: CVE-2021-46986
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46986
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc3: gadget: Free gadget structure only after freeing endpoints

As part of commit e81a7018d93a ("usb: dwc3: allocate gadget structure
dynamically") the dwc3_gadget_release() was added which will free
the dwc->gadget structure upon the device's removal when
usb_del_gadget_udc() is called in dwc3_gadget_exit().

However, simply freeing the gadget results a dangling pointer
situation: the endpoints created in dwc3_gadget_init_endpoints()
have their dep->endpoint.ep_list members chained off the list_head
anchored at dwc->gadget->ep_list.  Thus when dwc->gadget is freed,
the first dwc3_ep in the list now has a dangling prev pointer and
likewise for the next pointer of the dwc3_ep at the tail of the list.
The dwc3_gadget_free_endpoints() that follows will result in a
use-after-free when it calls list_del().

This was caught by enabling KASAN and performing a driver unbind.
The recent commit 568262bf5492 ("usb: dwc3: core: Add shutdown
callback for dwc3") also exposes this as a panic during shutdown.

There are a few possibilities to fix this.  One could be to perform
a list_del() of the gadget->ep_list itself which removes it from
the rest of the dwc3_ep chain.

Another approach is what this patch does, by splitting up the
usb_del_gadget_udc() call into its separate "del" and "put"
components.  This allows dwc3_gadget_free_endpoints() to be
called before the gadget is finally freed with usb_put_gadget().

## References
- https://git.kernel.org/stable/c/1ea775021282d90e1d08d696b7ab54aa75d688e5
- https://git.kernel.org/stable/c/b4b8e9601d7ee8806d2687f081a42485d27674a1
- https://git.kernel.org/stable/c/bb9c74a5bd1462499fe5ccb1e3c5ac40dcfa9139
- https://git.kernel.org/stable/c/bc0cdd72493236fb72b390ad38ce581e353c143c
