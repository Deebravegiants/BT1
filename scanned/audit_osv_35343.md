# [H] platform/x86: hp-bioscfg: Fix out-of-bounds array access in ACPI package parsing

## Summary
Severity: High
Advisory: CVE-2025-71101
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71101
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: hp-bioscfg: Fix out-of-bounds array access in ACPI package parsing

The hp_populate_*_elements_from_package() functions in the hp-bioscfg
driver contain out-of-bounds array access vulnerabilities.

These functions parse ACPI packages into internal data structures using
a for loop with index variable 'elem' that iterates through
enum_obj/integer_obj/order_obj/password_obj/string_obj arrays.

When processing multi-element fields like PREREQUISITES and
ENUM_POSSIBLE_VALUES, these functions read multiple consecutive array
elements using expressions like 'enum_obj[elem + reqs]' and
'enum_obj[elem + pos_values]' within nested loops.

The bug is that the bounds check only validated elem, but did not consider
the additional offset when accessing elem + reqs or elem + pos_values.

The fix changes the bounds check to validate the actual accessed index.

## References
- https://git.kernel.org/stable/c/79cab730dbaaac03b946c7f5681bd08c986e2abd
- https://git.kernel.org/stable/c/cf7ae870560b988247a4bbbe5399edd326632680
- https://git.kernel.org/stable/c/db4c26adf7117b1a4431d1197ae7109fee3230ad
- https://git.kernel.org/stable/c/e44c42c830b7ab36e3a3a86321c619f24def5206
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71101.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71101
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
