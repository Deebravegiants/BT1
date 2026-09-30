# [H] bpf: Fix helper writes to read-only maps

## Summary
Severity: High
Advisory: CVE-2024-49861
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49861
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <6.1.120, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix helper writes to read-only maps

Lonial found an issue that despite user- and BPF-side frozen BPF map
(like in case of .rodata), it was still possible to write into it from
a BPF program side through specific helpers having ARG_PTR_TO_{LONG,INT}
as arguments.

In check_func_arg() when the argument is as mentioned, the meta->raw_mode
is never set. Later, check_helper_mem_access(), under the case of
PTR_TO_MAP_VALUE as register base type, it assumes BPF_READ for the
subsequent call to check_map_access_type() and given the BPF map is
read-only it succeeds.

The helpers really need to be annotated as ARG_PTR_TO_{LONG,INT} | MEM_UNINIT
when results are written into them as opposed to read out of them. The
latter indicates that it's okay to pass a pointer to uninitialized memory
as the memory is written to anyway.

However, ARG_PTR_TO_{LONG,INT} is a special case of ARG_PTR_TO_FIXED_SIZE_MEM
just with additional alignment requirement. So it is better to just get
rid of the ARG_PTR_TO_{LONG,INT} special cases altogether and reuse the
fixed size memory types. For this, add MEM_ALIGNED to additionally ensure
alignment given these helpers write directly into the args via *<ptr> = val.
The .arg*_size has been initialized reflecting the actual sizeof(*<ptr>).

MEM_ALIGNED can only be used in combination with MEM_FIXED_SIZE annotated
argument types, since in !MEM_FIXED_SIZE cases the verifier does not know
the buffer size a priori and therefore cannot blindly write *<ptr> = val.

## References
- https://git.kernel.org/stable/c/1e75d25133158b525e0456876e9bcfd6b2993fd5
- https://git.kernel.org/stable/c/2ed98ee02d1e08afee88f54baec39ea78dc8a23c
- https://git.kernel.org/stable/c/32556ce93bc45c730829083cb60f95a2728ea48b
- https://git.kernel.org/stable/c/988e55abcf7fdb8fc9a76a7cf3f4e939a4d4fb3a
- https://git.kernel.org/stable/c/a2c8dc7e21803257e762b0bf067fd13e9c995da0
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49861.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49861
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
