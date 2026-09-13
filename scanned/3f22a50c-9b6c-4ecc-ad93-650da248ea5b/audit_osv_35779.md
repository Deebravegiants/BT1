# [H] Nomad Docker driver Linux host namespace bypass

## Summary
Severity: High
Advisory: CVE-2026-14373
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-14373
Type: osv

## Details
HashiCorp Nomad and Nomad Enterprise did not enforce the allow_privileged restriction for the Docker task driver's host namespace mode options. This may allow an authenticated job submitter to run a container in a host namespace and access information belonging to the host or to other workloads on the same client. This vulnerability, CVE-2026-14373, is fixed in Nomad Community Edition 2.0.4 and Nomad Enterprise 2.0.4, 1.11.8, and 1.10.14.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-19-nomad-docker-driver-vulnerable-to-host-namespace-bypass-on-linux/77557
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14373
- https://github.com/hashicorp/nomad
