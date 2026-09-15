# [H] bus: mhi: host: Range check CHDBOFF and ERDBOFF

## Summary
Severity: High
Advisory: CVE-2023-53598
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53598
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.192, >=5.11.0 <5.15.112, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bus: mhi: host: Range check CHDBOFF and ERDBOFF

If the value read from the CHDBOFF and ERDBOFF registers is outside the
range of the MHI register space then an invalid address might be computed
which later causes a kernel panic.  Range check the read value to prevent
a crash due to bad data from the device.

## References
- https://git.kernel.org/stable/c/2343385fe6eed11d0432ab42a97b3ca4aef06a99
- https://git.kernel.org/stable/c/372f1752b74572b0a9d2288841eab7db17daccae
- https://git.kernel.org/stable/c/4e584127ec2bd42a37c88badb49df409f21fa40a
- https://git.kernel.org/stable/c/6a0c637bfee69a74c104468544d9f2a6579626d0
- https://git.kernel.org/stable/c/83bf6b87e2dd053d95d89eb2f01ae885f9e568db
- https://git.kernel.org/stable/c/a2cbb1a45a0c86ce77839c0875414efe1a89315e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53598.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53598
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
