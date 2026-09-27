# [H] Bluechi: privilege escalation in bluechi via unrestricted cross-node systemd dependencies

## Summary
Severity: High
Advisory: CVE-2025-2515
CVSS: 7.2 (CVSS:3.1/AV:P/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-2515
Type: osv

## Details
A vulnerability was found in BlueChi, a multi-node systemd service controller used in RHIVOS. This flaw allows a user with root privileges on a managed node (qm) to create or override systemd service unit files that affect the host node. This issue can lead to privilege escalation, unauthorized service execution, and potential system compromise.

## References
- https://access.redhat.com/security/cve/CVE-2025-2515
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2515.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2515
- https://bugzilla.redhat.com/show_bug.cgi?id=2353313
- https://github.com/eclipse-bluechi/bluechi/issues/1069
- https://github.com/eclipse-bluechi/bluechi/commit/fe0d28301ce2bd45f0b1d8a98a94efef799fbc73#diff-64140c83db42a8888f346a40de293b80f79ebf7d75ce4137b22567e360bce607
- https://github.com/eclipse-bluechi/bluechi/pull/1073
- https://github.com/eclipse-bluechi/bluechi
