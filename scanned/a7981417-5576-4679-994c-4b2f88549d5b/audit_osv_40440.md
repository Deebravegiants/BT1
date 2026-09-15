# [H] accel/ivpu: Add bounds checks for firmware log indices

## Summary
Severity: High
Advisory: CVE-2026-53205
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53205
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.94, >=6.13.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Add bounds checks for firmware log indices

Add validation that read and write indices in the firmware log buffer
are within valid bounds (< data_size) before using them. If
out-of-bounds indices are encountered (from firmware), clamp them to
safe values instead of proceeding with invalid offsets.

This prevents potential out-of-bounds buffer access when firmware
supplies invalid log indices.

## References
- https://git.kernel.org/stable/c/535da9ad8420c3b686a642403d4147ff220255fd
- https://git.kernel.org/stable/c/5961c703414048f46818be8bbb11075a9a63fb4e
- https://git.kernel.org/stable/c/8ec70c0dbdf04392a26e03e38798a373934177be
- https://git.kernel.org/stable/c/dd1311bcf0e62f0c515115f46a3813370f4a4bb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53205.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53205
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
