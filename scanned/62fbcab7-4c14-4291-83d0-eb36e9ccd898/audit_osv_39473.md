# [H] Apache NimBLE: NULL pointer dereference vulnerability in SMP LTK request

## Summary
Severity: High
Advisory: CVE-2026-45816
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-45816
Type: osv

## Details
NULL Pointer Dereference vulnerability in Apache NimBLE in LE Long Term Key Request event.

This requires disabled asserts (otherwise assert would trigger before NULL dereference) and bogus (or misbehaving) controller, thus severity is low.

This issue affects Apache NimBLE: through 1.9.0.

Users are recommended to upgrade to version 1.10.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45816.json
- https://lists.apache.org/thread/psppdk5j8jnq1m4jn96tnfofspgqvzvn
- https://nvd.nist.gov/vuln/detail/CVE-2026-45816
- https://github.com/apache/mynewt-nimble/commit/9448c5f495eb55018121b24a9dab5305c9222ea1
