# [C] CVE-2021-47348

## Summary
Severity: Critical
Advisory: CVE-2021-47348
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47348
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Avoid HDCP over-read and corruption

Instead of reading the desired 5 bytes of the actual target field,
the code was reading 8. This could result in a corrupted value if the
trailing 3 bytes were non-zero, so instead use an appropriately sized
and zero-initialized bounce buffer, and read only 5 bytes before casting
to u64.

## References
- https://git.kernel.org/stable/c/c5b518f4b98dbb2bc31b6a55e6aaa1e0e2948f2e
- https://git.kernel.org/stable/c/06888d571b513cbfc0b41949948def6cb81021b2
- https://git.kernel.org/stable/c/3b2b93a485fb7a970bc8b5daef16f4cf579d172f
- https://git.kernel.org/stable/c/44c7c901cb368a9f2493748f213b247b5872639f
