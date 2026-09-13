# [C] Contiki-NG MQTT Client Out-of-Bounds Write in PUBLISH Topic Parser via Persistent State Between TCP Segments

## Summary
Severity: Critical
Advisory: CVE-2026-5857
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-5857
Type: osv

## Details
Contiki-NG's MQTT client parse_publish_vhdr() in os/net/app-layer/mqtt/mqtt.c sets topic_len_received=1 before checking topic_len against the 64-byte limit, so an over-length topic returns early but leaves the flag set. On the next TCP segment, tcp_input() re-invokes the parser with topic_received==0, and the persisted topic_len_received==1 skips the length-reading block containing the guard, falling through directly to a memcpy() that uses the unvalidated 16-bit topic_len as the copy length. The 65-byte topic[] destination overruns into adjacent struct fields including the payload_chunk pointer, which subsequent MQTT code dereferences, giving a compromised or attacker-controlled broker an arbitrary-pointer-write primitive. Contiki-NG's MQTT implementation has no TLS support so the connection is plaintext. Impact ranges from information disclosure and denial of service to remote code execution on embedded targets without memory protection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5857.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5857
- https://github.com/contiki-ng/contiki-ng/pull/3163
- https://github.com/contiki-ng/contiki-ng/commit/a34a2dbdc8bea784bd2ae5079aa4be520cd74f2d
- https://github.com/contiki-ng/contiki-ng
- https://y637f9qq2x.com/posts/cve-2026-5857/
