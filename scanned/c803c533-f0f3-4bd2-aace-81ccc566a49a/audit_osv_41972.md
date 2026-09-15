# [H] drm/amd/display: Validate payload length and link_index in dc_process_dmub_aux_transfer_async

## Summary
Severity: High
Advisory: CVE-2026-64219
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64219
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Validate payload length and link_index in dc_process_dmub_aux_transfer_async

[Why&How]
dc_process_dmub_aux_transfer_async() copies payload->length bytes into a
16-byte stack buffer (dpaux.data[16]) guarded only by an ASSERT(), which
is a no-op in release builds. If a caller ever passes length > 16 this
results in a stack buffer overflow via memcpy.

Additionally, link_index is used to dereference dc->links[] without
bounds checking against dc->link_count, risking an out-of-bounds access.

Replace the ASSERT with a hard runtime check that returns false when
payload->length exceeds the destination buffer size, and add a bounds
check for link_index before it is used.

(cherry picked from commit ba4caa9fecdf7a38f98c878ad05a8a64148b6881)

## References
- https://git.kernel.org/stable/c/16a5fa57565afb6bf37e18129921c270c93d8e2b
- https://git.kernel.org/stable/c/1c8c6e912f2945b2a3e669afca6b52174b88e86e
- https://git.kernel.org/stable/c/1ecde19bfce6535bffddad1139ff466b6d401b8e
- https://git.kernel.org/stable/c/3265f3ed373fb8048be713aadcdf702579a0e53d
- https://git.kernel.org/stable/c/6c92f6d9600efa3ef0d9e560a2b52776d9803c29
- https://git.kernel.org/stable/c/90c398e822ca76e40548df0c061dd4f93ea92d71
- https://git.kernel.org/stable/c/d6590e3f766e3111dd1beaf88b9384d117acfa6b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64219.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64219
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
