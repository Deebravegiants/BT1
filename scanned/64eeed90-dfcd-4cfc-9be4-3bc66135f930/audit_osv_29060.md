# [M] Eclipse Mosquito: Double free vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-3935
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2024-10-30
Source: https://osv.dev/vulnerability/CVE-2024-3935
Type: osv

## Details
In Eclipse Mosquito, versions from 2.0.0 through 2.0.18, if a Mosquitto broker is configured to create an outgoing bridge connection, and that bridge connection has an incoming topic configured that makes use of topic remapping, then if the remote connection sends a crafted PUBLISH packet to the broker a double free will occur with a subsequent crash of the broker.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3935.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3935
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/197
- https://github.com/eclipse-mosquitto/mosquitto/commit/ae7a804dadac8f2aaedb24336df8496a9680fda9
- https://github.com/eclipse/mosquitto
- https://mosquitto.org/blog/2024/10/version-2-0-19-released/
