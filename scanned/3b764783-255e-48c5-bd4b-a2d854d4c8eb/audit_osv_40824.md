# [M] Openssh: local mitm of x11 forwarding via abstract unix socket pre-binding in red hat enterprise linux openssh client versions

## Summary
Severity: Medium
Advisory: CVE-2026-55655
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-55655
Type: osv

## Details
A flaw was found in OpenSSH. A local unprivileged attacker on a Linux client host can hijack client-side X11 forwarding connections. This is possible by pre-binding the preferred abstract X socket name when X11 forwarding is enabled and a local UNIX-domain X socket is used. A successful attack can compromise the confidentiality of forwarded X11 traffic, including sensitive window contents and input, and may allow some manipulation of the forwarded session.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:36759
- https://access.redhat.com/errata/RHSA-2026:47755
- https://access.redhat.com/errata/RHSA-2026:47756
- https://access.redhat.com/errata/RHSA-2026:47757
- https://access.redhat.com/errata/RHSA-2026:54387
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/security/cve/CVE-2026-55655
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55655.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55655
- https://bugzilla.redhat.com/show_bug.cgi?id=2462250
