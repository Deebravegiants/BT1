# [M] CVE-2021-47195

## Summary
Severity: Medium
Advisory: CVE-2021-47195
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47195
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: fix use-after-free of the add_lock mutex

Commit 6098475d4cb4 ("spi: Fix deadlock when adding SPI controllers on
SPI buses") introduced a per-controller mutex. But mutex_unlock() of
said lock is called after the controller is already freed:

  spi_unregister_controller(ctlr)
  -> put_device(&ctlr->dev)
    -> spi_controller_release(dev)
  -> mutex_unlock(&ctrl->add_lock)

Move the put_device() after the mutex_unlock().

## References
- https://git.kernel.org/stable/c/11eab327a2a8bd36c38afbff920ae1bd45588dd4
- https://git.kernel.org/stable/c/54c2c96eafcfd242e52e932ab54ace4784efe1dd
- https://git.kernel.org/stable/c/6c53b45c71b4920b5e62f0ea8079a1da382b9434
- https://git.kernel.org/stable/c/37330f37f6666c7739a44b2b6b95b047ccdbed2d
