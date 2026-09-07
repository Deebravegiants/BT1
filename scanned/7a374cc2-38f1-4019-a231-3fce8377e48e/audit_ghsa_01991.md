# [M] Improper network isolation in Hashicorp Nomad

## Summary
Severity: Medium
Advisory: GHSA-vf6q-9f2f-mwhv
CVE: CVE-2021-32575
CWE: CWE-1100
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-24
Source: https://github.com/advisories/GHSA-vf6q-9f2f-mwhv
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=1.0.0 <1.0.5
- Go: `github.com/hashicorp/nomad` — affected >=0 <0.12.12

## Details
HashiCorp Nomad and Nomad Enterprise up to version 1.0.4 bridge networking mode allows ARP spoofing from other bridged tasks on the same node. Fixed in 0.12.12, 1.0.5, and 1.1.0 RC1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32575
- https://discuss.hashicorp.com/t/hcsec-2021-14-nomad-bridge-networking-mode-allows-arp-spoofing-from-other-bridged-tasks-on-same-node/24296
- https://www.hashicorp.com/blog/category/nomad
