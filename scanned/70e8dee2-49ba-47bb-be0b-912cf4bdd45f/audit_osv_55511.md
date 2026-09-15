# [H] CVE-2025-62490

## Summary
Severity: High
Advisory: CVE-2025-62490
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-62490
Type: osv

## Details
In quickjs, in js_print_object, when printing an array, the function first fetches the array length and then loops over it. The issue is, printing a value is not side-effect free. An attacker-defined callback could run during js_print_value, during which the array could get resized and len1 become out of bounds. This results in a use-after-free.A second instance occurs in the same function during printing of a map or set objects. The code iterates over ms->records list, but once again, elements could be removed from the list during js_print_value call.

## References
- https://bellard.org/quickjs/Changelog
- https://issuetracker.google.com/434196651
