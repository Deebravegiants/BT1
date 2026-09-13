# [H] CVE-2021-47653

## Summary
Severity: High
Advisory: CVE-2021-47653
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47653
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: davinci: vpif: fix use-after-free on driver unbind

The driver allocates and registers two platform device structures during
probe, but the devices were never deregistered on driver unbind.

This results in a use-after-free on driver unbind as the device
structures were allocated using devres and would be freed by driver
core when remove() returns.

Fix this by adding the missing deregistration calls to the remove()
callback and failing probe on registration errors.

Note that the platform device structures must be freed using a proper
release callback to avoid leaking associated resources like device
names.

## References
- https://git.kernel.org/stable/c/b5a3bb7f6f164eb6ee74ef4898dcd019b2063448
- https://git.kernel.org/stable/c/43acb728bbc40169d2e2425e84a80068270974be
- https://git.kernel.org/stable/c/6512c3c39cb6b573b791ce45365818a38b76afbe
- https://git.kernel.org/stable/c/9ffc602e14d7b9f7e7cb2f67e18dfef9ef8af676
