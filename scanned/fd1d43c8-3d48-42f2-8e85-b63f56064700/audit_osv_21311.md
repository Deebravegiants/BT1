# [H] CVE-2021-4206

## Summary
Severity: High
Advisory: CVE-2021-4206
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-04-29
Source: https://osv.dev/vulnerability/CVE-2021-4206
Type: osv

## Details
A flaw was found in the QXL display device emulation in QEMU. An integer overflow in the cursor_alloc() function can lead to the allocation of a small cursor object followed by a subsequent heap-based buffer overflow. This flaw allows a malicious privileged guest user to crash the QEMU process on the host or potentially execute arbitrary code within the context of the QEMU process.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20250321-0010/
- https://www.debian.org/security/2022/dsa-5133
- https://bugzilla.redhat.com/show_bug.cgi?id=2036998
- https://starlabs.sg/advisories/21-4206/
