# [M] CVE-2021-47416

## Summary
Severity: Medium
Advisory: CVE-2021-47416
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47416
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: mdio: fix memory leak

Syzbot reported memory leak in MDIO bus interface, the problem was in
wrong state logic.

MDIOBUS_ALLOCATED indicates 2 states:
	1. Bus is only allocated
	2. Bus allocated and __mdiobus_register() fails, but
	   device_register() was called

In case of device_register() has been called we should call put_device()
to correctly free the memory allocated for this device, but mdiobus_free()
calls just kfree(dev) in case of MDIOBUS_ALLOCATED state

To avoid this behaviour we need to set bus->state to MDIOBUS_UNREGISTERED
_before_ calling device_register(), because put_device() should be
called even in case of device_register() failure.

## References
- https://git.kernel.org/stable/c/0d2dd40a7be61b89a7c99dae8ee96389d27b413a
- https://git.kernel.org/stable/c/2250392d930bd0d989f24d355d6355b0150256e7
- https://git.kernel.org/stable/c/2397b9e118721292429fea8807a698e71b94795f
- https://git.kernel.org/stable/c/25e9f88c7e3cc35f5e3d3db199660d28a15df639
- https://git.kernel.org/stable/c/414bb4ead1362ef2c8592db723c017258f213988
- https://git.kernel.org/stable/c/ca6e11c337daf7925ff8a2aac8e84490a8691905
- https://git.kernel.org/stable/c/f4f502a04ee1e543825af78f47eb7785015cd9f6
- https://git.kernel.org/stable/c/064c2616234a7394867c924b5c1303974f3a4f4d
