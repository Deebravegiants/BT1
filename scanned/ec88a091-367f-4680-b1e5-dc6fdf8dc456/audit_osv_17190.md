# [C] CVE-2020-13556

## Summary
Severity: Critical
Advisory: CVE-2020-13556
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-13556
Type: osv

## Details
An out-of-bounds write vulnerability exists in the Ethernet/IP server functionality of EIP Stack Group OpENer 2.3 and development commit 8c73bf3. A specially crafted series of network requests can lead to remote code execution. An attacker can send a sequence of requests to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1170
