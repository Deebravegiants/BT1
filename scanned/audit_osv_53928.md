# [M] CVE-2023-32570

## Summary
Severity: Medium
Advisory: CVE-2023-32570
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-10
Source: https://osv.dev/vulnerability/CVE-2023-32570
Type: osv

## Details
VideoLAN dav1d before 1.2.0 has a thread_task.c race condition that can lead to an application crash, related to dav1d_decode_frame_exit.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3WGSO7UMOF4MVLQ5H6KIV7OG6ONS377B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LXZ6CUNJFDJLCFOZHY2TIGMCAEITLCRP/
- https://code.videolan.org/videolan/dav1d/-/tags/1.2.0
- https://security.gentoo.org/glsa/202310-05
- https://code.videolan.org/videolan/dav1d/-/commit/cf617fdae0b9bfabd27282854c8e81450d955efa
