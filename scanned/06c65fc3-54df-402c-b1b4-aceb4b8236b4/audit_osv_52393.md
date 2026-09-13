# [M] CVE-2021-47401

## Summary
Severity: Medium
Advisory: CVE-2021-47401
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47401
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipack: ipoctal: fix stack information leak

The tty driver name is used also after registering the driver and must
specifically not be allocated on the stack to avoid leaking information
to user space (or triggering an oops).

Drivers should not try to encode topology information in the tty device
name but this one snuck in through staging without anyone noticing and
another driver has since copied this malpractice.

Fixing the ABI is a separate issue, but this at least plugs the security
hole.

## References
- https://git.kernel.org/stable/c/a89936cce87d60766a75732a9e7e25c51164f47c
- https://git.kernel.org/stable/c/acb96e782bad427ca4bb1bd94af660acd1462380
- https://git.kernel.org/stable/c/0a9c36a2e06a249acbed64e8e0b84637c2ad7575
- https://git.kernel.org/stable/c/2725925982dc96a78069cd118ea3d66759bfdad7
- https://git.kernel.org/stable/c/5f6a309a699675680df15d9b6d389114515b4426
- https://git.kernel.org/stable/c/741ea2670e021350e54f491106bdaa22dc50e6a0
- https://git.kernel.org/stable/c/829f13d6079cf7a2465522f39acb43033e9b320d
- https://git.kernel.org/stable/c/8657158a3b68c85234e6da3d8eae33d6183588b7
