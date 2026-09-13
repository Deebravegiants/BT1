# [H] CVE-2021-47404

## Summary
Severity: High
Advisory: CVE-2021-47404
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47404
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: betop: fix slab-out-of-bounds Write in betop_probe

Syzbot reported slab-out-of-bounds Write bug in hid-betopff driver.
The problem is the driver assumes the device must have an input report but
some malicious devices violate this assumption.

So this patch checks hid_device's input is non empty before it's been used.

## References
- https://git.kernel.org/stable/c/6fc4476dda58f6c00097c7ddec3b772513f57525
- https://git.kernel.org/stable/c/708107b80aa616976d1c5fa60ac0c1390749db5e
- https://git.kernel.org/stable/c/a4faa7153b87fbcfe4be15f4278676f79ca6e019
- https://git.kernel.org/stable/c/bb8b72374db69afa25a5b65cf1c092860c6fe914
- https://git.kernel.org/stable/c/dedfc35a2de2bae9fa3da8210a05bfd515f83fee
- https://git.kernel.org/stable/c/fe9bb925e7096509711660d39c0493a1546e9550
- https://git.kernel.org/stable/c/1c83c38dec83d57bc18d0c01d82c413d3b34ccb9
- https://git.kernel.org/stable/c/1e4ce418b1cb1a810256b5fb3fd33d22d1325993
