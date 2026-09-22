# [H] firmware: arm_scmi: Harden accesses to the reset domains

## Summary
Severity: High
Advisory: CVE-2022-48655
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48655
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.277, >=5.5.0 <5.10.218, >=5.11.0 <5.15.71, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_scmi: Harden accesses to the reset domains

Accessing reset domains descriptors by the index upon the SCMI drivers
requests through the SCMI reset operations interface can potentially
lead to out-of-bound violations if the SCMI driver misbehave.

Add an internal consistency check before any such domains descriptors
accesses.

## References
- https://git.kernel.org/stable/c/1f08a1b26cfc53b7715abc46857c6023bb1b87de
- https://git.kernel.org/stable/c/7184491fc515f391afba23d0e9b690caaea72daf
- https://git.kernel.org/stable/c/8e65edf0d37698f7a6cb174608d3ec7976baf49e
- https://git.kernel.org/stable/c/e9076ffbcaed5da6c182b144ef9f6e24554af268
- https://git.kernel.org/stable/c/f2277d9e2a0d092c13bae7ee82d75432bb8b5108
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48655.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48655
- https://security.netapp.com/advisory/ntap-20240912-0008/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
