# [H] ASoC: codec: sma1307: Fix memory corruption in sma1307_setting_loaded()

## Summary
Severity: High
Advisory: CVE-2025-39935
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39935
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codec: sma1307: Fix memory corruption in sma1307_setting_loaded()

The sma1307->set.header_size is how many integers are in the header
(there are 8 of them) but instead of allocating space of 8 integers
we allocate 8 bytes.  This leads to memory corruption when we copy data
it on the next line:

        memcpy(sma1307->set.header, data,
               sma1307->set.header_size * sizeof(int));

Also since we're immediately copying over the memory in ->set.header,
there is no need to zero it in the allocator.  Use devm_kmalloc_array()
to allocate the memory instead.

## References
- https://git.kernel.org/stable/c/78338108b5a856dc98223a335f147846a8a18c51
- https://git.kernel.org/stable/c/cd59ca8f75dbb42a67fcae975c766114644e36c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39935.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39935
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
