# [C] Arbitrary File Write in Ansible Playbooks leads to RCE in Jumpserver

## Summary
Severity: Critical
Advisory: CVE-2024-40629
Aliases: GHSA-3wgp-q8m7-v33v
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-18
Source: https://osv.dev/vulnerability/CVE-2024-40629
Type: osv

## Details
JumpServer is an open-source Privileged Access Management (PAM) tool that provides DevOps and IT teams with on-demand and secure access to SSH, RDP, Kubernetes, Database and RemoteApp endpoints through a web browser. An attacker can exploit the Ansible playbook to write arbitrary files, leading to remote code execution (RCE) in the Celery container. The Celery container runs as root and has database access, allowing an attacker to steal all secrets for hosts, create a new JumpServer account with admin privileges, or manipulate the database in other ways. This issue has been patched in release versions 3.10.12 and 4.0.0. It is recommended to upgrade the safe versions. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40629.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-3wgp-q8m7-v33v
- https://nvd.nist.gov/vuln/detail/CVE-2024-40629
- https://www.sonarsource.com/blog/diving-into-jumpserver-attackers-gateway-to-internal-networks-2-2
