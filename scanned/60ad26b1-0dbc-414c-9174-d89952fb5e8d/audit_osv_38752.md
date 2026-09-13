# [M] CVE-2026-42006

## Summary
Severity: Medium
Advisory: CVE-2026-42006
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-42006
Type: osv

## Details
An attacker can cause uncontrolled memory usage with excessive bracing over IMAP. The fix in CVE-2026-27857 was incomplete, only blocking one way of doing this, so there was still another way left open. In particular, the fix was for closing braces, but you could still use open braces to bypass the limit. Using excessive bracing, attacker can cause memory usage up to configured memory limit. Install fixed version, or configure vsz_limit for imap process to low value. No publicly available exploits are known.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42006.json
- https://access.redhat.com/errata/RHSA-2026:41905
- https://access.redhat.com/errata/RHSA-2026:41988
- https://access.redhat.com/errata/RHSA-2026:42091
- https://access.redhat.com/errata/RHSA-2026:44355
- https://access.redhat.com/errata/RHSA-2026:44357
- https://access.redhat.com/errata/RHSA-2026:44373
- https://access.redhat.com/errata/RHSA-2026:46379
- https://access.redhat.com/errata/RHSA-2026:46380
- https://access.redhat.com/errata/RHSA-2026:46381
- https://access.redhat.com/errata/RHSA-2026:46532
- https://access.redhat.com/errata/RHSA-2026:49513
- https://access.redhat.com/security/cve/CVE-2026-42006
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0002.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42006.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42006
- https://bugzilla.redhat.com/show_bug.cgi?id=2476476
