# [M] bpftool: Fix NULL pointer dereference when pin {PROG, MAP, LINK} without FILE

## Summary
Severity: Medium
Advisory: CVE-2022-49875
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49875
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpftool: Fix NULL pointer dereference when pin {PROG, MAP, LINK} without FILE

When using bpftool to pin {PROG, MAP, LINK} without FILE,
segmentation fault will occur. The reson is that the lack
of FILE will cause strlen to trigger NULL pointer dereference.
The corresponding stacktrace is shown below:

do_pin
  do_pin_any
    do_pin_fd
      mount_bpffs_for_pin
        strlen(name) <- NULL pointer dereference

Fix it by adding validation to the common process.

## References
- https://git.kernel.org/stable/c/34de8e6e0e1f66e431abf4123934a2581cb5f133
- https://git.kernel.org/stable/c/6dcdd1b68b7f9333d48d48fc77b75e7f235f6a4a
- https://git.kernel.org/stable/c/8c80b2fca4112d724dde477aed13f7b0510a2792
- https://git.kernel.org/stable/c/da5161ba94c5e9182c301dd4f09c94f715c068bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49875.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49875
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
