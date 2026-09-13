# [M] Nomad vulnerable to arbitrary file read/write on client host through symlink attack

## Summary
Severity: Medium
Advisory: CVE-2026-6959
Aliases: GHSA-3934-423w-4jq3, GO-2026-5076
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-6959
Type: osv

## Details
HashiCorp Nomad and Nomad Enterprise prior to 2.0.1 are vulnerable to arbitrary file read and write on the client host as the Nomad process user through a symlink attack. This vulnerability (CVE-2026-6959) is fixed in Nomad 2.0.1, 1.11.5 and 1.10.11.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-14-nomad-arbitrary-file-read-write-on-client-host-through-symlink-attack/77416
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6959.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6959
- https://github.com/hashicorp/nomad
