# [C] CVE-2018-4059

## Summary
Severity: Critical
Advisory: CVE-2018-4059
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-4059
Type: osv

## Details
An exploitable unsafe default configuration vulnerability exists in the TURN server function of coTURN prior to version 4.5.0.9. By default, the TURN server runs an unauthenticated telnet admin portal on the loopback interface. This can provide administrator access to the TURN server configuration, which can lead to additional attacks. An attacker who can get access to the telnet port can gain administrator access to the TURN server.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2018-0733
