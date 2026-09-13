# [M] Contiki-NG DNS/mDNS Resolver Out-of-Bounds Read via Unchecked skip_name Traversal Before Transaction-ID Validation

## Summary
Severity: Medium
Advisory: CVE-2026-5856
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-5856
Type: osv

## Details
Contiki-NG's DNS/mDNS resolver skip_name() in os/services/resolv/resolv.c walks DNS wire-format name labels with no packet-boundary check, and the caller in newdata() invokes it in a loop iterating nquestions times from the attacker-controlled DNS header before validating the transaction ID. An attacker who sets nquestions higher than the number of complete questions present causes skip_name() to walk past the UDP packet buffer, and the returned pointer is cast to struct dns_answer * for further memory reads. On builds with RESOLV_CONF_SUPPORTS_MDNS enabled, any peer on the local segment can trigger the read unauthenticated via a multicast UDP 5353 packet with no outstanding query required; on standard DNS builds an attacker who can inject a UDP response from port 53 during an outstanding query can trigger the same read. Impact is out-of-bounds read of uip_buf and adjacent memory, disclosing memory contents or crashing the resolver.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5856.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5856
- https://github.com/contiki-ng/contiki-ng/pull/3169
- https://github.com/contiki-ng/contiki-ng/commit/04a3f0a0067d2ee87d1f297b6d0f4392d8c98ffe
- https://github.com/contiki-ng/contiki-ng
