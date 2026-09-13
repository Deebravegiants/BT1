# [H] CVE-2021-46965

## Summary
Severity: High
Advisory: CVE-2021-46965
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46965
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: physmap: physmap-bt1-rom: Fix unintentional stack access

Cast &data to (char *) in order to avoid unintentionally accessing
the stack.

Notice that data is of type u32, so any increment to &data
will be in the order of 4-byte chunks, and this piece of code
is actually intended to be a byte offset.

Addresses-Coverity-ID: 1497765 ("Out-of-bounds access")

## References
- https://git.kernel.org/stable/c/34ec706bf0b7c4ca249a729c1bcb91f706c7a7be
- https://git.kernel.org/stable/c/4d786870e3262ec098a3b4ed10b895176bc66ecb
- https://git.kernel.org/stable/c/4e4ebb827bf09311469ffd9d0c14ed40ed9747aa
- https://git.kernel.org/stable/c/683313993dbe1651c7aa00bb42a041d70e914925
