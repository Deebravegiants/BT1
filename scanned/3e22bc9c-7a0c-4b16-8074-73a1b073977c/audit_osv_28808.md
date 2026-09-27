# [H] CVE-2024-36856

## Summary
Severity: High
Advisory: CVE-2024-36856
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-12
Source: https://osv.dev/vulnerability/CVE-2024-36856
Type: osv

## Details
RMQTT Broker 0.4.0 is vulnerable to Denial of Service (DoS) due to improper session resource management. An attacker can exhaust system memory and crash the daemon by establishing and maintaining a vast number of long-lived malicious publish/subscribe sessions.

## References
- https://gist.github.com/pengwGit/d8410afeb0d5d11ab79f596a32178c2e
- https://github.com/rmqtt/rmqtt/releases/tag/0.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36856.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36856
