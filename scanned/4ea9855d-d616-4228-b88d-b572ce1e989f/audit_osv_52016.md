# [H] CVE-2021-46966

## Summary
Severity: High
Advisory: CVE-2021-46966
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46966
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: custom_method: fix potential use-after-free issue

In cm_write(), buf is always freed when reaching the end of the
function.  If the requested count is less than table.length, the
allocated buffer will be freed but subsequent calls to cm_write() will
still try to access it.

Remove the unconditional kfree(buf) at the end of the function and
set the buf to NULL in the -EINVAL error path to match the rest of
function.

## References
- https://git.kernel.org/stable/c/1d53ca5d131074c925ce38361fb0376d3bf7e394
- https://git.kernel.org/stable/c/72814a94c38a33239793f7622cec6ace1e540c4b
- https://git.kernel.org/stable/c/a5b26a2e362f572d87e9fd35435680e557052a17
- https://git.kernel.org/stable/c/b7a5baaae212a686ceb812c32fceed79c03c0234
- https://git.kernel.org/stable/c/f16737caf41fc06cfe6e49048becb09657074d4b
- https://git.kernel.org/stable/c/62dc2440ebb552aa0d7f635e1697e077d9d21203
- https://git.kernel.org/stable/c/8b04d57f30caf76649d0567551589af9a66ca9be
- https://git.kernel.org/stable/c/90575d1d9311b753cf1718f4ce9061ddda7dfd23
- https://git.kernel.org/stable/c/e483bb9a991bdae29a0caa4b3a6d002c968f94aa
