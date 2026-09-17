# [H] CVE-2018-4058

## Summary
Severity: High
Advisory: CVE-2018-4058
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-4058
Type: osv

## Details
An exploitable unsafe default configuration vulnerability exists in the TURN server functionality of coTURN prior to 4.5.0.9. By default, the TURN server allows relaying external traffic to the loopback interface of its own host. This can provide access to other private services running on that host, which can lead to further attacks. An attacker can set up a relay with a loopback address as the peer on an affected TURN server to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2018-0732
