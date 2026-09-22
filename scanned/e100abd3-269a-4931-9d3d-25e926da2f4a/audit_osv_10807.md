# [C] CVE-2017-2891

## Summary
Severity: Critical
Advisory: CVE-2017-2891
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-2891
Type: osv

## Details
An exploitable use-after-free vulnerability exists in the HTTP server implementation of Cesanta Mongoose 6.8. An ordinary HTTP POST request with a CGI target can cause a reuse of previously freed pointer potentially resulting in remote code execution. An attacker needs to send this HTTP request over the network to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0398
