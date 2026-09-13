# [M] drm/amd/display: Check if modulo is 0 before dividing.

## Summary
Severity: Medium
Advisory: CVE-2022-49294
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49294
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Check if modulo is 0 before dividing.

[How & Why]
If a value of 0 is read, then this will cause a divide-by-0 panic.

## References
- https://git.kernel.org/stable/c/07efce8269a038c37814eb656b4de14aa3015fc6
- https://git.kernel.org/stable/c/10ef82d6e0af5536ec64770c07f6bbabfdd6977c
- https://git.kernel.org/stable/c/49947b906a6bd9668eaf4f9cf691973c25c26955
- https://git.kernel.org/stable/c/96725758eff7b3805e4e94d1443a100757412720
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49294.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49294
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
