# [M] CVE-2019-5020

## Summary
Severity: Medium
Advisory: CVE-2019-5020
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-5020
Type: osv

## Details
An exploitable denial of service vulnerability exists in the object lookup functionality of Yara 3.8.1. A specially crafted binary file can cause a negative value to be read to satisfy an assert, resulting in Denial of Service. An attacker can create a malicious binary to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0781
