# [H] CVE-2020-11068

## Summary
Severity: High
Advisory: CVE-2020-11068
Aliases: GHSA-559p-6xgm-fpv9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-23
Source: https://osv.dev/vulnerability/CVE-2020-11068
Type: osv

## Details
In LoRaMac-node before 4.4.4, a reception buffer overflow can happen due to the received buffer size not being checked. This has been fixed in 4.4.4.

## References
- https://github.com/Lora-net/LoRaMac-node/commit/e3063a91daa7ad8a687223efa63079f0c24568e4
- https://github.com/Lora-net/LoRaMac-node/security/advisories/GHSA-559p-6xgm-fpv9
