# [H] Udisks2: udisks2: local privilege escalation via as-user option spoofing

## Summary
Severity: High
Advisory: CVE-2026-7867
Aliases: GHSA-j42g-v9jw-6ph3
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-7867
Type: osv

## Details
A flaw was found in udisks2. A local attacker with an active console session can exploit insufficient authorization checking on the 'as-user' option in the org.freedesktop.UDisks2.Filesystem.Mount() D-Bus method. This allows the attacker to spoof the 'as-user' parameter, mounting filesystems on behalf of arbitrary users, including privileged accounts. This can lead to local privilege escalation through mount point injection and manipulation of the mount namespace visible to privileged users.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/storaged-project/udisks/releases/tag/udisks-2.11.2
- https://access.redhat.com/errata/RHSA-2026:53435
- https://access.redhat.com/errata/RHSA-2026:64798
- https://access.redhat.com/security/cve/CVE-2026-7867
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7867.json
- https://github.com/storaged-project/udisks/security/advisories/GHSA-j42g-v9jw-6ph3
- https://nvd.nist.gov/vuln/detail/CVE-2026-7867
- https://bugzilla.redhat.com/show_bug.cgi?id=2466747
- https://github.com/storaged-project/udisks
