# [M] AppArmor Base Profile Misconfiguration in snapd Permits Confined Snaps Unauthorized Access to Hashed Passwords via systemd-userdbd

## Summary
Severity: Medium
Advisory: CVE-2024-5300
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2024-5300
Type: osv

## Details
An access control bypass and information disclosure vulnerability exists in the base AppArmor security profile configuration of Canonical snapd. The abstraction rules located in /etc/apparmor.d/abstractions/nss-systemd (inherited via ) inadvertently permit strictly confined snap applications, which lack the privileged account-control interface, to interact directly with the io.systemd.Multiplexer and io.systemd.NameServiceSwitch UNIX domain sockets under /run/systemd/userdb/.
On systems where the systemd-userdbd service is installed and operational, the service fails to distinguish between an unconfined root user on the host system and a restricted root user running within a snap application's sandbox (such as a daemon or configuration hook). Because systemd-userdbd returns "complete" user records—including sensitive hashed user passwords from /etc/shadow—when queried by a process running as root, a compromised or malicious strictly confined snap executing code as root can successfully query the Varlink interface to retrieve all system password hashes, bypassing intended snap sandbox restrictions. This issue is mitigated by the fact that systemd-userdbd is not installed by default on standard Ubuntu deployments.

## References
- https://github.com/canonical
- https://github.com/canonical/snapd/
- https://launchpad.net/ubuntu/+source/snapd
- https://launchpad.net/ubuntu/bionic
- https://launchpad.net/ubuntu/focal
- https://launchpad.net/ubuntu/jammy
- https://launchpad.net/ubuntu/noble
- https://launchpad.net/ubuntu/resolute
- https://launchpad.net/ubuntu/xenial
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5300.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5300
- https://ubuntu.com/security/CVE-2024-5300
