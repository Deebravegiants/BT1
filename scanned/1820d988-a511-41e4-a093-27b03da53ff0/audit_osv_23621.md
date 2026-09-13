# [M] drm/amd/display: Call dc_stream_release for remove link enc assignment

## Summary
Severity: Medium
Advisory: CVE-2022-49233
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49233
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Call dc_stream_release for remove link enc assignment

[Why]
A porting error resulted in the stream assignment for the link
being retained without being released - a memory leak.

[How]
Fix the porting error by adding back the dc_stream_release() intended
as part of the original patch.

## References
- https://git.kernel.org/stable/c/a28b7b6a0c827ce672edcdb5b2b5916b0beebe03
- https://git.kernel.org/stable/c/f2bde8349c35d01d7c50456ea06a5c7d5e0e5ed0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49233.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
