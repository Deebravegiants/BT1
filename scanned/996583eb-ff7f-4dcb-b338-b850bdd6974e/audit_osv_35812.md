# [M] Nomad vulnerable to cross-namespace host volume claim deletion

## Summary
Severity: Medium
Advisory: CVE-2026-14896
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-14896
Type: osv

## Details
HashiCorp Nomad and Nomad Enterprise are vulnerable to a cross-namespace authorization bypass in the dynamic host volumes feature that may allow an operator holding the host volume delete permission in one namespace to delete a sticky volume claim belonging to a job in another namespace. This vulnerability, CVE-2026-14896, is fixed in Nomad Community Edition 2.0.4 and Nomad Enterprise 2.0.4, 1.11.8, and 1.10.14.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-22-nomad-vulnerable-to-cross-namespace-host-volume-claim-deletion/77562
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14896.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14896
- https://github.com/hashicorp/nomad
