# [M] Pika Unauthenticated Replication Access via Internal Protobuf Port

## Summary
Severity: Medium
Advisory: CVE-2026-84700
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84700
Type: osv

## Details
PikiwiDB (Pika) v3.5.7 exposes an internal protobuf replication server on a port derived from the client port plus 2000 (e.g. 11221 when the default client port 9221 is used) that does not authenticate incoming requests. Although requirepass is intended to gate replication — a slave presents it as masterauth inside its MetaSync request — only the MetaSync handler (HandleMetaSyncRequest) validates it; the frame dispatcher (DealMessage) does not require a completed or attempted MetaSync before routing other message types to their handlers. As a result, an unauthenticated remote attacker can connect directly to the replication port and issue TrySync, DBSync, BinlogSync, and RemoveSlaveNode requests, obtaining the full-sync snapshot and live write stream and removing replica nodes, even when requirepass is configured.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84700.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84700
- https://www.vulncheck.com/advisories/pika-unauthenticated-replication-access-via-internal-protobuf-port
- https://github.com/OpenAtomFoundation/pikiwidb/issues/3270
- https://github.com/OpenAtomFoundation/pikiwidb
- https://github.com/OpenAtomFoundation/pikiwidb/blob/v3.5.7/src/pika_repl_server_conn.cc
