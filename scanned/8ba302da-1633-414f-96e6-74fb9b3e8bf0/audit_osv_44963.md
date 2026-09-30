# [H] snap-confine Local Privilege Escalation via Capabilities Misconfiguration or Flaw in Execution Environment Setup

## Summary
Severity: High
Advisory: CVE-2026-8933
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-8933
Type: osv

## Details
A local privilege escalation vulnerability exists in snap-confine, a set-capabilities core component used internally by Canonical snapd to construct the secure execution environment for snap applications. This vulnerability uniquely affects versions of snap-confine configured with set-capabilities (rather than standard set-uid-root installations).
Due to a flaw in how privilege boundaries or security sandboxes are initialized when the binary runs under limited ambient capabilities, a local, unprivileged attacker can exploit this behavior to bypass intended restrictions and execute arbitrary code. Successful exploitation allows the local user to elevate their privileges to full root authority.

## References
- https://github.com/canonical
- https://github.com/canonical/snapd/
- https://launchpad.net/ubuntu/+source/snapd
- https://launchpad.net/ubuntu/jammy
- https://launchpad.net/ubuntu/noble
- https://launchpad.net/ubuntu/resolute
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8933.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8933
- https://ubuntu.com/security/CVE-2026-8933
