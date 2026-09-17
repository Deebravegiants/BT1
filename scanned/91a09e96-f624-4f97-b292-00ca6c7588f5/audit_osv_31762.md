# [H] NFC: nci: Add bounds checking in nci_hci_create_pipe()

## Summary
Severity: High
Advisory: CVE-2025-21735
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21735
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFC: nci: Add bounds checking in nci_hci_create_pipe()

The "pipe" variable is a u8 which comes from the network.  If it's more
than 127, then it results in memory corruption in the caller,
nci_hci_connect_gate().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/10b3f947b609713e04022101f492d288a014ddfa
- https://git.kernel.org/stable/c/110b43ef05342d5a11284cc8b21582b698b4ef1c
- https://git.kernel.org/stable/c/172cdfc3a5ea20289c58fb73dadc6fd4a8784a4e
- https://git.kernel.org/stable/c/2ae4bade5a64d126bd18eb66bd419005c5550218
- https://git.kernel.org/stable/c/59c7ed20217c0939862fbf8145bc49d5b3a13f4f
- https://git.kernel.org/stable/c/674e17c5933779a8bf5c15d596fdfcb5ccdebbc2
- https://git.kernel.org/stable/c/bd249109d266f1d52548c46634a15b71656e0d44
- https://git.kernel.org/stable/c/d5a461c315e5ff92657f84d8ba50caa5abf5c22a
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21735.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21735
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
