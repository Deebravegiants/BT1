# [H] drm/xe: Fix potential integer overflow in page size calculation

## Summary
Severity: High
Advisory: CVE-2024-42066
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42066
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Fix potential integer overflow in page size calculation

Explicitly cast tbo->page_alignment to u64 before bit-shifting to
prevent overflow when assigning to min_page_size.

## References
- https://git.kernel.org/stable/c/4f4fcafde343a54465f85a2909fc684918507a4b
- https://git.kernel.org/stable/c/79d54ddf0e292b810887994bb04709c5ac0e1531
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42066.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42066
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
