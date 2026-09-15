# [C] JumpServer's insecure Ansible playbook validation leads to RCE in Celery

## Summary
Severity: Critical
Advisory: CVE-2024-29201
Aliases: GHSA-pjpp-cm9x-6rwj
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-03-29
Source: https://osv.dev/vulnerability/CVE-2024-29201
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. Attackers can bypass the input validation mechanism in JumpServer's Ansible to execute arbitrary code within the Celery container. Since the Celery container runs with root privileges and has database access, attackers could steal sensitive information from all hosts or manipulate the database. This vulnerability is fixed in v3.10.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29201.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-pjpp-cm9x-6rwj
- https://nvd.nist.gov/vuln/detail/CVE-2024-29201
- https://www.sonarsource.com/blog/diving-into-jumpserver-attackers-gateway-to-internal-networks-2-2
