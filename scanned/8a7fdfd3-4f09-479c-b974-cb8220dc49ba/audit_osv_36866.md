# [H] Udisks: missing authorization check allows unprivileged users to restore luks headers via udisks d-bus api

## Summary
Severity: High
Advisory: CVE-2026-26103
Aliases: GHSA-c75h-phf8-ccjm
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-26103
Type: osv

## Details
A flaw was found in the udisks storage management daemon that exposes a privileged D-Bus API for restoring LUKS encryption headers without proper authorization checks. The issue allows a local unprivileged user to instruct the root-owned udisks daemon to overwrite encryption metadata on block devices. This can permanently invalidate encryption keys and render encrypted volumes inaccessible. Successful exploitation results in a denial-of-service condition through irreversible data loss.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-26103.json
- https://access.redhat.com/errata/RHSA-2026:3476
- https://access.redhat.com/errata/RHSA-2026:5831
- https://access.redhat.com/security/cve/CVE-2026-26103
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26103.json
- https://github.com/storaged-project/udisks/security/advisories/GHSA-c75h-phf8-ccjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-26103
- https://bugzilla.redhat.com/show_bug.cgi?id=2433719
