# [H] umatiGateway's UI publicly accessible in provided docker-compose file

## Summary
Severity: High
Advisory: CVE-2025-27615
Aliases: GHSA-qf9w-x9qx-2mq7
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-03-10
Source: https://osv.dev/vulnerability/CVE-2025-27615
Type: osv

## Details
umatiGateway is software for connecting OPC Unified Architecture servers with an MQTT broker utilizing JSON messages. The user interface may possibly be publicly accessible with umatiGateway's provided docker-compose file. With this access, the configuration can be viewed and altered. Commit 5d81a3412bc0051754a3095d89a06d6d743f2b16 uses `127.0.0.1:8080:8080` to limit access to the local network. For those who are unable to use this proposed patch, a firewall on Port 8080 may block remote access, but the workaround may not be perfect because Docker may also bypass a firewall by its iptable based rules for port forwarding.

## References
- https://github.com/umati/umatiGateway/blob/abe73096a17307327f0d6dc0ed4db1fb93464521/README.md?plain=1#L34-L35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27615.json
- https://github.com/umati/umatiGateway/security/advisories/GHSA-qf9w-x9qx-2mq7
- https://nvd.nist.gov/vuln/detail/CVE-2025-27615
- https://github.com/umati/umatiGateway/commit/5d81a3412bc0051754a3095d89a06d6d743f2b16
- https://github.com/umati/umatiGateway/pull/101
