# [M] drm/bridge: Add missing pm_runtime_put_sync

## Summary
Severity: Medium
Advisory: CVE-2022-49128
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49128
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/bridge: Add missing pm_runtime_put_sync

pm_runtime_get_sync() will increase the rumtime PM counter
even when it returns an error. Thus a pairing decrement is needed
to prevent refcount leak. Fix this by replacing this API with
pm_runtime_resume_and_get(), which will not change the runtime
PM counter on error. Besides, a matching decrement is needed
on the error handling path to keep the counter balanced.

## References
- https://git.kernel.org/stable/c/46f47807738441e354873546dde0b000106c068a
- https://git.kernel.org/stable/c/792533e54cd6e89191798ccd1abd590c62b9077e
- https://git.kernel.org/stable/c/9df80dc738926a2ea4bd1ce5993c3d0f4b0e855c
- https://git.kernel.org/stable/c/ff13c90d7f7ab606b37be6d15140d19013d6736c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49128.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49128
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
