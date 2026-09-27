# [H] CVE-2021-47282

## Summary
Severity: High
Advisory: CVE-2021-47282
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47282
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: bcm2835: Fix out-of-bounds access with more than 4 slaves

Commit 571e31fa60b3 ("spi: bcm2835: Cache CS register value for
->prepare_message()") limited the number of slaves to 3 at compile-time.
The limitation was necessitated by a statically-sized array prepare_cs[]
in the driver private data which contains a per-slave register value.

The commit sought to enforce the limitation at run-time by setting the
controller's num_chipselect to 3:  Slaves with a higher chipselect are
rejected by spi_add_device().

However the commit neglected that num_chipselect only limits the number
of *native* chipselects.  If GPIO chipselects are specified in the
device tree for more than 3 slaves, num_chipselect is silently raised by
of_spi_get_gpio_numbers() and the result are out-of-bounds accesses to
the statically-sized array prepare_cs[].

As a bandaid fix which is backportable to stable, raise the number of
allowed slaves to 24 (which "ought to be enough for anybody"), enforce
the limitation on slave ->setup and revert num_chipselect to 3 (which is
the number of native chipselects supported by the controller).
An upcoming for-next commit will allow an arbitrary number of slaves.

## References
- https://git.kernel.org/stable/c/01415ff85a24308059e06ca3e97fd7bf75648690
- https://git.kernel.org/stable/c/13817d466eb8713a1ffd254f537402f091d48444
- https://git.kernel.org/stable/c/82a8ffba54d31e97582051cb56ba1f988018681e
- https://git.kernel.org/stable/c/b5502580cf958b094f3b69dfe4eece90eae01fbc
