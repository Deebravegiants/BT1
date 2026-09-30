# [M] FreeRDP has a Heap-use-after-free in cam_v4l_stream_capture_thread

## Summary
Severity: Medium
Advisory: CVE-2026-24678
Aliases: GHSA-6gvg-29wx-6v7h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24678
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, A capture thread sends sample responses using a freed channel callback after a device channel close, leading to a use after free in ecam_channel_write. This vulnerability is fixed in 3.22.0.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24678.json
- https://access.redhat.com/errata/RHSA-2026:19033
- https://access.redhat.com/errata/RHSA-2026:3068
- https://access.redhat.com/errata/RHSA-2026:4121
- https://access.redhat.com/security/cve/CVE-2026-24678
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24678.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-6gvg-29wx-6v7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-24678
- https://bugzilla.redhat.com/show_bug.cgi?id=2438197
- https://github.com/FreeRDP/FreeRDP/commit/f3ab1a16139036179d9852745fdade18fec11600
