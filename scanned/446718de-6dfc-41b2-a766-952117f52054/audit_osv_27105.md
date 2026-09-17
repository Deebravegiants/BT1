# [H] Eclipse Mosquito: Heap Buffer Overflow in my_subscribe_callback

## Summary
Severity: High
Advisory: CVE-2024-10525
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-10-30
Source: https://osv.dev/vulnerability/CVE-2024-10525
Type: osv

## Details
In Eclipse Mosquitto, from version 1.3.2 through 2.0.18, if a malicious broker sends a crafted SUBACK packet with no reason codes, a client using libmosquitto may make out of bounds memory access when acting in its on_subscribe callback. This affects the mosquitto_sub and mosquitto_rr clients.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10525.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10525
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/190
- https://github.com/eclipse-mosquitto/mosquitto/commit/8ab20b4ba4204fdcdec78cb4d9f03c944a6e0e1c
- https://github.com/eclipse/mosquitto
- https://mosquitto.org/blog/2024/10/version-2-0-19-released/
