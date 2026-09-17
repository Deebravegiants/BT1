# [M] CVE-2021-47172

## Summary
Severity: Medium
Advisory: CVE-2021-47172
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47172
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ad7124: Fix potential overflow due to non sequential channel numbers

Channel numbering must start at 0 and then not have any holes, or
it is possible to overflow the available storage.  Note this bug was
introduced as part of a fix to ensure we didn't rely on the ordering
of child nodes.  So we need to support arbitrary ordering but they all
need to be there somewhere.

Note I hit this when using qemu to test the rest of this series.
Arguably this isn't the best fix, but it is probably the most minimal
option for backporting etc.

Alexandru's sign-off is here because he carried this patch in a larger
set that Jonathan then applied.

## References
- https://git.kernel.org/stable/c/26da8040eccc6c6b0e415e9a3baf72fd39eb2fdc
- https://git.kernel.org/stable/c/f2a772c51206b0c3f262e4f6a3812c89a650191b
- https://git.kernel.org/stable/c/f49149964d2423fb618fb6b755bb1eaa431cca2c
- https://git.kernel.org/stable/c/f70122825076117787b91e7f219e21c09f11a5b9
