# [H] drm/xe/pf: Don't attempt to process FAST_REQ or EVENT relays

## Summary
Severity: High
Advisory: CVE-2026-72360
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72360
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/pf: Don't attempt to process FAST_REQ or EVENT relays

Currently defined VF/PF relay actions use regular REQUEST messages
only and the PF shouldn't attempt to handle FAST_REQUEST nor EVENT
messages as this would result in breaking the VFPF ABI protocol
and also might trigger an assert on the PF side.

(cherry picked from commit 1714d360fc5ae2e0886a69e979095d9c7ff3568a)

## References
- https://git.kernel.org/stable/c/499be4b5d64209e9f18c9442f9fbeef7155ae900
- https://git.kernel.org/stable/c/a4208d8032abd7f591581994f31e23b80b8fe659
- https://git.kernel.org/stable/c/adc7dda728ca3e340a413e3bbc10cf159e1866a4
- https://git.kernel.org/stable/c/ed8b0d731892c68b41ecbd27c952af284816dec1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72360.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72360
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
