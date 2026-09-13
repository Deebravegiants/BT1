# [H] Glib: integer overflow in g_string_maybe_expand() leading to potential buffer overflow in glib gstring

## Summary
Severity: High
Advisory: BIT-java-2025-6052
Aliases: BIT-java-min-2025-6052, BIT-jre-2025-6052, CVE-2025-6052
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-6052
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.481

## Details
A flaw was found in how GLib’s GString manages memory when adding data to strings. If a string is already very large, combining it with more input can cause a hidden overflow in the size calculation. This makes the system think it has enough memory when it doesn’t. As a result, data may be written past the end of the allocated memory, leading to crashes or memory corruption.

## References
- https://access.redhat.com/security/cve/CVE-2025-6052
- https://bugzilla.redhat.com/show_bug.cgi?id=2372666
- https://nvd.nist.gov/vuln/detail/CVE-2025-6052
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://openjdk.org/groups/vulnerability/advisories/2026-01-20
- https://www.oracle.com/security-alerts/cpuapr2026.html
- https://www.oracle.com/security-alerts/cpujan2026.html
