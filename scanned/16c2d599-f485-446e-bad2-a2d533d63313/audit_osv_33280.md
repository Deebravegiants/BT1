# [H] bpf: Check the helper function is valid in get_helper_proto

## Summary
Severity: High
Advisory: CVE-2025-39990
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39990
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Check the helper function is valid in get_helper_proto

kernel test robot reported verifier bug [1] where the helper func
pointer could be NULL due to disabled config option.

As Alexei suggested we could check on that in get_helper_proto
directly. Marking tail_call helper func with BPF_PTR_POISON,
because it is unused by design.

  [1] https://lore.kernel.org/oe-lkp/202507160818.68358831-lkp@intel.com

## References
- https://git.kernel.org/stable/c/3d429cb1278e995e22995ef117fa96d223a67e93
- https://git.kernel.org/stable/c/6233715b4b714068d6c831d214a4e8792109875a
- https://git.kernel.org/stable/c/e4414b01c1cd9887bbde92f946c1ba94e40d6d64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39990.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
