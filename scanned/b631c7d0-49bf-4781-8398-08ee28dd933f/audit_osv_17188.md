# [H] CVE-2020-13530

## Summary
Severity: High
Advisory: CVE-2020-13530
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-13530
Type: osv

## Details
A denial-of-service vulnerability exists in the Ethernet/IP server functionality of the EIP Stack Group OpENer 2.3 and development commit 8c73bf3. A large number of network requests in a small span of time can cause the running program to stop. An attacker can send a sequence of requests to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1143
