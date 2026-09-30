# [H] DietPi-Dashboard Insufficient TLS Handshake Pool

## Summary
Severity: High
Advisory: CVE-2023-38505
Aliases: GHSA-3jr4-9rxf-fr44
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-27
Source: https://osv.dev/vulnerability/CVE-2023-38505
Type: osv

## Details
DietPi-Dashboard is a web dashboard for the operating system DietPi. The dashboard only allows for one TLS handshake to be in process at a given moment. Once a TCP connection is established in HTTPS mode, it will assume that it should be waiting for a handshake, and will stay this way indefinitely until a handshake starts or some error occurs. In version 0.6.1, this can be exploited by simply not starting the handshake, preventing any other TLS handshakes from getting through. An attacker can lock the dashboard in a state where it is waiting for a TLS handshake from the attacker, who won't provide it. This prevents any legitimate traffic from getting to the dashboard, and can last indefinitely. Version 0.6.2 has a patch for this issue. As a workaround, do not use HTTPS mode on the open internet where anyone can connect. Instead, put a reverse proxy in front of the dashboard, and have it handle any HTTPS connections.

## References
- https://asciinema.org/a/8nRKbdf7AkPLmP3QxFZUSmPwp?t=7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38505.json
- https://github.com/ravenclaw900/DietPi-Dashboard/security/advisories/GHSA-3jr4-9rxf-fr44
- https://nvd.nist.gov/vuln/detail/CVE-2023-38505
- https://github.com/ravenclaw900/DietPi-Dashboard/commit/79cd78615d28f577454415e4baafe4dcd9d09666
- https://github.com/ravenclaw900/DietPi-Dashboard/pull/606
