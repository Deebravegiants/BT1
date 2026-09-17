# [H] accel/ivpu: Add buffer overflow check in MS get_info_ioctl

## Summary
Severity: High
Advisory: CVE-2026-53203
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53203
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Add buffer overflow check in MS get_info_ioctl

Add validation that the info size returned from the metric stream info
query is not exceeded when checked against the allocated buffer size.
If the firmware returns a size larger than the buffer, reject the
operation with -EOVERFLOW instead of proceeding with an incorrect
buffer copy.

## References
- https://git.kernel.org/stable/c/4e5047cc94bea1cc7b670b7f503358e9af0542df
- https://git.kernel.org/stable/c/d3c12ed33e8923f3090909a1738f3e59292996a6
- https://git.kernel.org/stable/c/fa598556ecef412edcb391f144b7642e18fdfd45
- https://git.kernel.org/stable/c/fb176425837693f50c5c9fc8db6fbb04af22bd0a
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53203.json
- https://access.redhat.com/security/cve/CVE-2026-53203
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53203.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53203
- https://bugzilla.redhat.com/show_bug.cgi?id=2492798
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
