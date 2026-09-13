# [H] Udisks: out-of-bounds read in udisks daemon

## Summary
Severity: High
Advisory: CVE-2025-8067
CVSS: 8.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:H)
Published: 2025-08-28
Source: https://osv.dev/vulnerability/CVE-2025-8067
Type: osv

## Details
A flaw was found in the Udisks daemon, where it allows unprivileged users to create loop devices using the D-BUS system. This is achieved via the loop device handler, which handles requests sent through the D-BUS interface. As two of the parameters of this handle, it receives the file descriptor list and index specifying the file where the loop device should be backed. The function itself validates the index value to ensure it isn't bigger than the maximum value allowed. However, it fails to validate the lower bound, allowing the index parameter to be a negative value. Under these circumstances, an attacker can cause the UDisks daemon to crash or perform a local privilege escalation by gaining access to files owned by privileged users.

## References
- http://www.openwall.com/lists/oss-security/2025/08/28/1
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/08/msg00023.html
- https://access.redhat.com/errata/RHSA-2025:15017
- https://access.redhat.com/errata/RHSA-2025:15018
- https://access.redhat.com/errata/RHSA-2025:15020
- https://access.redhat.com/errata/RHSA-2025:15956
- https://access.redhat.com/errata/RHSA-2025:16021
- https://access.redhat.com/errata/RHSA-2025:16090
- https://access.redhat.com/errata/RHSA-2025:16106
- https://access.redhat.com/errata/RHSA-2025:16121
- https://access.redhat.com/errata/RHSA-2025:16122
- https://access.redhat.com/errata/RHSA-2025:16125
- https://access.redhat.com/errata/RHSA-2025:16130
- https://access.redhat.com/security/cve/CVE-2025-8067
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/8xxx/CVE-2025-8067.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-8067
- https://bugzilla.redhat.com/show_bug.cgi?id=2388623
- https://github.com/storaged-project/udisks
