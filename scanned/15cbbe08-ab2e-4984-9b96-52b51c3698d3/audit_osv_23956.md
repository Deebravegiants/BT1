# [M] ata: libata-core: fix NULL pointer deref in ata_host_alloc_pinfo()

## Summary
Severity: Medium
Advisory: CVE-2022-49731
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49731
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <4.9.320, >=4.10.0 <4.14.285, >=4.15.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ata: libata-core: fix NULL pointer deref in ata_host_alloc_pinfo()

In an unlikely (and probably wrong?) case that the 'ppi' parameter of
ata_host_alloc_pinfo() points to an array starting with a NULL pointer,
there's going to be a kernel oops as the 'pi' local variable won't get
reassigned from the initial value of NULL. Initialize 'pi' instead to
'&ata_dummy_port_info' to fix the possible kernel oops for good...

Found by Linux Verification Center (linuxtesting.org) with the SVACE static
analysis tool.

## References
- https://git.kernel.org/stable/c/07cbdb4807d369fbda73062a91b570c4dc5ec429
- https://git.kernel.org/stable/c/1ac5efee33f29e704226506d429b84575a5d66f8
- https://git.kernel.org/stable/c/253334f84c81bc6a43af489f108c0bddad989eef
- https://git.kernel.org/stable/c/36cd19e7d4e5571d77a2ed20c5b6ef50cf57734a
- https://git.kernel.org/stable/c/a810bd5af06977a847d1f202b22d7defd5c62497
- https://git.kernel.org/stable/c/bf476fe22aa1851bab4728e0c49025a6a0bea307
- https://git.kernel.org/stable/c/ca4693e6e06e4fd2b240c0fec47aa2498c94848e
- https://git.kernel.org/stable/c/ff128fbea720bf763fa345680dda5f050bc24a47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49731.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49731
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
