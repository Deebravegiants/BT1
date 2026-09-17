# [H] cifs: some missing initializations on replay

## Summary
Severity: High
Advisory: CVE-2026-31693
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-31693
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.128, >=6.7.0 <6.12.75, >=6.8.0 <6.18.16, >=6.13.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: some missing initializations on replay

In several places in the code, we have a label to signify
the start of the code where a request can be replayed if
necessary. However, some of these places were missing the
necessary reinitializations of certain local variables
before replay.

This change makes sure that these variables get initialized
after the label.

## References
- https://git.kernel.org/stable/c/14f66f44646333d2bfd7ece36585874fd72f8286
- https://git.kernel.org/stable/c/1d731e512134495e0ef490ade0e4d91dc0d515ec
- https://git.kernel.org/stable/c/7c9ce68192eef14c777cb6ce17155d2eb2431aea
- https://git.kernel.org/stable/c/c854ab481ece4b3e5f4c2e8b22824f015ff874a5
- https://git.kernel.org/stable/c/c99e160938b627f6f28edee930e8abc157e84386
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31693.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31693
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
