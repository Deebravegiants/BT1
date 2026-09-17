# [M] ASoC: mxs: Fix error handling in mxs_sgtl5000_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49242
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49242
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: mxs: Fix error handling in mxs_sgtl5000_probe

This function only calls of_node_put() in the regular path.
And it will cause refcount leak in error paths.
For example, when codec_np is NULL, saif_np[0] and saif_np[1]
are not NULL, it will cause leaks.

of_node_put() will check if the node pointer is NULL, so we can
call it directly to release the refcount of regular pointers.

## References
- https://git.kernel.org/stable/c/44acdaf7acb60054d872bed18ce0e7db8ce900ce
- https://git.kernel.org/stable/c/67e12f1cb2f97468c12b59e21975eaa0f332e7d2
- https://git.kernel.org/stable/c/6ae0a4d8fec551ec581d620f0eb1fe31f755551c
- https://git.kernel.org/stable/c/790d2628e3fcc819d8f5572eb5615113fb2e727a
- https://git.kernel.org/stable/c/86b6cf989437e694fd0a15782b5a513853a739e0
- https://git.kernel.org/stable/c/8d880226c86f37624e2a5f3c6d92ac0ec3375f96
- https://git.kernel.org/stable/c/d2923b48d99fe663cb93d8b481c93299fcd68656
- https://git.kernel.org/stable/c/f16ad2c0e22687f80e5981c67374023f51c204b9
- https://git.kernel.org/stable/c/f8d38056bcd220ea6f0802a5586d1a12ebcce849
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49242.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49242
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
