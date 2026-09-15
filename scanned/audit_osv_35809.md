# [H] Nomad vulnerable to sandbox escape in Docker task driver

## Summary
Severity: High
Advisory: CVE-2026-14891
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-14891
Type: osv

## Details
HashiCorp Nomad and Nomad Enterprise are vulnerable to a sandbox escape in the Docker task driver that may allow a job submitter to bind-mount a host path into a container even when volume bind mounts are disabled, potentially leading to reading and writing files on the host. This vulnerability, CVE-2026-14891, is fixed in Nomad Community Edition 2.0.4 and Nomad Enterprise 2.0.4, 1.11.8, and 1.10.14.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-21-nomad-vulnerable-to-sandbox-escape-in-docker-task-driver/77561
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14891.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14891
- https://github.com/hashicorp/nomad
