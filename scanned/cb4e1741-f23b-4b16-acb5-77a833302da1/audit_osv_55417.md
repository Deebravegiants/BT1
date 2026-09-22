# [H] CVE-2025-45333

## Summary
Severity: High
Advisory: CVE-2025-45333
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-45333
Type: osv

## Details
berkeley-abc abc 1.1 contains a Null Pointer Dereference (NPD) vulnerability in the Abc_NtkCecFraigPart function of its data processing module, leading to unpredictable program behavior, causing segmentation faults, and program crashes.

## References
- https://github.com/berkeley-abc/abc/pull/383
- https://gist.github.com/QiuYitai/eb49750fe58e39ce685cfd87a41eacb9
