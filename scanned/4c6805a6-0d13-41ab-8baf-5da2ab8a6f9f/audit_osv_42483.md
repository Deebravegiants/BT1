# [H] drm/amdkfd: Check bounds on CRIU restore queue type and mqd size

## Summary
Severity: High
Advisory: CVE-2026-68258
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68258
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Check bounds on CRIU restore queue type and mqd size

We weren't checking whether the values provided in the private
data in kfd CRIU restore were within bounds.

For queue type, add a KFD_QUEUE_TYPE_MAX and ensure the provided
type is less than it.

For mqd_size, add new function mqd_size_from_queue_type and confirm
that the provided mqd_size matches expectations.

(cherry picked from commit f19d8086f6644083c913d70bfdeee20e1b6f46a5)

## References
- https://git.kernel.org/stable/c/47ea05f246bebc81c7796f56265cffd812cf0601
- https://git.kernel.org/stable/c/cc10a5839756982504ee8568fc1e1625962ab7f8
- https://git.kernel.org/stable/c/fd1691ec62701c982ea32e749678988c67fd4c21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68258.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68258
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
