# [H] drm/amdgpu: validate doorbell_offset in user queue creation

## Summary
Severity: High
Advisory: CVE-2026-31766
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31766
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: validate doorbell_offset in user queue creation

amdgpu_userq_get_doorbell_index() passes the user-provided
doorbell_offset to amdgpu_doorbell_index_on_bar() without bounds
checking. An arbitrarily large doorbell_offset can cause the
calculated doorbell index to fall outside the allocated doorbell BO,
potentially corrupting kernel doorbell space.

Validate that doorbell_offset falls within the doorbell BO before
computing the BAR index, using u64 arithmetic to prevent overflow.

(cherry picked from commit de1ef4ffd70e1d15f0bf584fd22b1f28cbd5e2ec)

## References
- https://git.kernel.org/stable/c/3543005a42d7e8e12b21897ef6798541bf7cbcd3
- https://git.kernel.org/stable/c/86b732fbc37ce4fb76cdd4af0fb7e30a6acdbce6
- https://git.kernel.org/stable/c/a018d1819f158991b7308e4f74609c6c029b670c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31766.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31766
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
