# [H] Openssh: possible remote code execution due to a race condition in signal handling affecting red hat enterprise linux 9

## Summary
Severity: High
Advisory: CVE-2024-6409
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/CVE-2024-6409
Type: osv

## Details
A race condition vulnerability was discovered in how signals are handled by OpenSSH's server (sshd). If a remote attacker does not authenticate within a set time period, then sshd's SIGALRM handler is called asynchronously. However, this signal handler calls various functions that are not async-signal-safe, for example, syslog(). As a consequence of a successful attack, in the worst case scenario, an attacker may be able to perform a remote code execution (RCE) as an unprivileged user running the sshd server.

## References
- http://www.openwall.com/lists/oss-security/2024/07/08/2
- http://www.openwall.com/lists/oss-security/2024/07/09/2
- http://www.openwall.com/lists/oss-security/2024/07/09/5
- http://www.openwall.com/lists/oss-security/2024/07/10/1
- http://www.openwall.com/lists/oss-security/2024/07/10/2
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://explore.alas.aws.amazon.com/CVE-2024-6409.html
- https://security-tracker.debian.org/tracker/CVE-2024-6409
- https://sig-security.rocky.page/issues/CVE-2024-6409/
- https://ubuntu.com/security/CVE-2024-6409
- https://www.openssh.com/
- https://www.suse.com/security/cve/CVE-2024-6409.html
- https://access.redhat.com/errata/RHSA-2024:4457
- https://access.redhat.com/errata/RHSA-2024:4613
- https://access.redhat.com/errata/RHSA-2024:4716
- https://access.redhat.com/errata/RHSA-2024:4910
- https://access.redhat.com/errata/RHSA-2024:4955
- https://access.redhat.com/errata/RHSA-2024:4960
- https://access.redhat.com/errata/RHSA-2024:5444
