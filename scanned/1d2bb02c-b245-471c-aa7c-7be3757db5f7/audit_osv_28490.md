# [H] efi: libstub: only free priv.runtime_map when allocated

## Summary
Severity: High
Advisory: CVE-2024-33619
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-33619
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

efi: libstub: only free priv.runtime_map when allocated

priv.runtime_map is only allocated when efi_novamap is not set.
Otherwise, it is an uninitialized value.  In the error path, it is freed
unconditionally.  Avoid passing an uninitialized value to free_pool.
Free priv.runtime_map only when it was allocated.

This bug was discovered and resolved using Coverity Static Analysis
Security Testing (SAST) by Synopsys, Inc.

## References
- https://git.kernel.org/stable/c/4b2543f7e1e6b91cfc8dd1696e3cdf01c3ac8974
- https://git.kernel.org/stable/c/6ca67a5fe1c606d1fbe24c30a9fc0bdc43a18554
- https://git.kernel.org/stable/c/9dce01f386c9ce6990c0a83fa14b1c95330b037e
- https://git.kernel.org/stable/c/b8938d6f570f010a1dcdbfed3e5b5d3258c2a908
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33619.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33619
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
