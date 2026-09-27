# [M] CVE-2020-28348

## Summary
Severity: Medium
Advisory: CVE-2020-28348
Aliases: GHSA-5x92-p4p5-33c4, GO-2022-0770
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/CVE-2020-28348
Type: osv

## Details
HashiCorp Nomad and Nomad Enterprise 0.9.0 up to 0.12.7 client Docker file sandbox feature may be subverted when not explicitly disabled or when using a volume mount type. Fixed in 0.12.8, 0.11.7, and 0.10.8.

## References
- https://github.com/hashicorp/nomad/blob/master/CHANGELOG.md#0128-november-10-2020
- https://github.com/hashicorp/nomad/issues/9303
