# [H] Local Privilege Escalation in snapd

## Summary
Severity: High
Advisory: CVE-2026-3888
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-3888
Type: osv

## Details
Local privilege escalation in snapd on Linux allows local attackers to get root privilege by re-creating snap's private /tmp directory when systemd-tmpfiles is configured to automatically clean up this directory. This issue affects Ubuntu 16.04 LTS, 18.04 LTS, 20.04 LTS, 22.04 LTS, and 24.04 LTS.

## References
- http://www.openwall.com/lists/oss-security/2026/03/18/1
- https://github.com/canonical
- https://github.com/canonical/snapd/
- https://launchpad.net/ubuntu/+source/snapd
- https://launchpad.net/ubuntu/bionic
- https://launchpad.net/ubuntu/focal
- https://launchpad.net/ubuntu/jammy
- https://launchpad.net/ubuntu/noble
- https://launchpad.net/ubuntu/xenial
- https://cdn2.qualys.com/advisory/2026/03/17/snap-confine-systemd-tmpfiles.txt
- https://discourse.ubuntu.com/t/snapd-local-privilege-escalation-cve-2026-3888
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3888.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3888
- https://ubuntu.com/security/notices/USN-8102-1
- https://ubuntu.com/security/CVE-2026-3888
- https://blog.qualys.com/vulnerabilities-threat-research/2026/03/17/cve-2026-3888-important-snap-flaw-enables-local-privilege-escalation-to-root
