# [H] scsi: aacraid: Fix double-free on probe failure

## Summary
Severity: High
Advisory: CVE-2024-46673
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46673
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <4.19.321, >=4.20.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.108, >=6.2.0 <6.6.49, >=6.7.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: aacraid: Fix double-free on probe failure

aac_probe_one() calls hardware-specific init functions through the
aac_driver_ident::init pointer, all of which eventually call down to
aac_init_adapter().

If aac_init_adapter() fails after allocating memory for aac_dev::queues,
it frees the memory but does not clear that member.

After the hardware-specific init function returns an error,
aac_probe_one() goes down an error path that frees the memory pointed to
by aac_dev::queues, resulting.in a double-free.

## References
- https://git.kernel.org/stable/c/4b540ec7c0045c2d01c4e479f34bbc8f147afa4c
- https://git.kernel.org/stable/c/564e1986b00c5f05d75342f8407f75f0a17b94df
- https://git.kernel.org/stable/c/60962c3d8e18e5d8dfa16df788974dd7f35bd87a
- https://git.kernel.org/stable/c/85449b28ff6a89c4513115e43ddcad949b5890c9
- https://git.kernel.org/stable/c/8a3995a3ffeca280a961b59f5c99843d81b15929
- https://git.kernel.org/stable/c/919ddf8336f0b84c0453bac583808c9f165a85c2
- https://git.kernel.org/stable/c/9e96dea7eff6f2bbcd0b42a098012fc66af9eb69
- https://git.kernel.org/stable/c/d237c7d06ffddcdb5d36948c527dc01284388218
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46673.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46673
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
