# [C] Arbitrary File Read in Ansible Playbooks in Jumpserver

## Summary
Severity: Critical
Advisory: CVE-2024-40628
Aliases: GHSA-rpf7-g4xh-84v9
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-18
Source: https://osv.dev/vulnerability/CVE-2024-40628
Type: osv

## Details
JumpServer is an open-source Privileged Access Management (PAM) tool that provides DevOps and IT teams with on-demand and secure access to SSH, RDP, Kubernetes, Database and RemoteApp endpoints through a web browser. An attacker can exploit the ansible playbook to read arbitrary files in the celery container, leading to sensitive information disclosure. The Celery container runs as root and has database access, allowing the attacker to steal all secrets for hosts, create a new JumpServer account with admin privileges, or manipulate the database in other ways. This issue has been addressed in release versions 3.10.12 and 4.0.0. It is recommended to upgrade the safe versions. There is no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40628.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-rpf7-g4xh-84v9
- https://nvd.nist.gov/vuln/detail/CVE-2024-40628
- https://www.sonarsource.com/blog/diving-into-jumpserver-attackers-gateway-to-internal-networks-2-2
