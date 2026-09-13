# [C] s390/mm: Fix handling of _PAGE_UNUSED pte bit

## Summary
Severity: Critical
Advisory: CVE-2026-72412
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72412
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/mm: Fix handling of _PAGE_UNUSED pte bit

The _PAGE_UNUSED softbit should not really be lying around. Its sole
purpose is to signal to try_to_unmap_one() and try_to_migrate_one()
that the page can be discarded instead of being moved / swapped.

KVM has no way to know why a page is being unmapped, so it sets the bit
on userspace ptes corresponding to unused guest pages every time they
get unmapped. KVM has no reasonable way to clear the bit once the page
is in use again.

While set_ptes() checks and clears the bit, other paths that set new
ptes did not. This led to used pages being thrown out as if they were
unused, causing guest corruption.

Fix the issue by clearing the _PAGE_UNUSED bit for present ptes in
set_pte(), i.e. whenever a present pte is getting set. The check in
set_ptes() is then redundant and can be removed.

Also fix gmap_helper_try_set_pte_unused() to only set the bit if the
pte is present; the _PAGE_UNUSED bit is only defined for present ptes
and thus should not be set for non-present ptes.

## References
- https://git.kernel.org/stable/c/d4bb00704a66024502261fa7a523c07420249fea
- https://git.kernel.org/stable/c/fda07c8e4b54b9105f1ca73f0adea7b244d405f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72412.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72412
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
