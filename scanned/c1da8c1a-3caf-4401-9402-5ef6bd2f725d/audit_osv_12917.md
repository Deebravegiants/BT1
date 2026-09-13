# [M] CVE-2018-16359

## Summary
Severity: Medium
Advisory: CVE-2018-16359
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2018-09-02
Source: https://osv.dev/vulnerability/CVE-2018-16359
Type: osv

## Details
Google gVisor before 2018-08-23, within the seccomp sandbox, permits access to the renameat system call, which allows attackers to rename files on the host OS.

## References
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1632
- https://github.com/google/gvisor/commit/001a4c2493b13a43d62c7511fb509a959ae4abc2
