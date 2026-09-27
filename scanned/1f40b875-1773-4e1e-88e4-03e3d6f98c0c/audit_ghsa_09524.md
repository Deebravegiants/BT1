# [M] OpenTelemetry eBPF Instrumentation: CPU-mismatch fallback uses 256-byte buffer with 8KB size

## Summary
Severity: Medium
Advisory: GHSA-r6c9-g6q5-qrf9
CVE: CVE-2026-45681
CWE: CWE-125, CWE-130
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-r6c9-g6q5-qrf9
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0 <0.9.0

## Details
### Summary

The per-CPU message-buffer fallback path uses a 256-byte backup buffer but preserves the original payload size, which can be up to 8KB. If a CPU mismatch occurs, OBI can read beyond the fallback buffer and leak adjacent memory into telemetry.

### Details

https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/032473449b53d9f02ec4619d4f5b84e6a81db362/bpf/common/http_buf_size.h#L4-L7

`k_kprobes_http2_buf_size` is defined as 256 bytes, the size of the fallback buffer.

https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/032473449b53d9f02ec4619d4f5b84e6a81db362/bpf/common/msg_buffer.h#L12-L36

Introduces 8KB per-CPU buffer and 256-byte `fallback_buf` in `msg_buffer_t`, creating a size mismatch for fallback use.

https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/032473449b53d9f02ec4619d4f5b84e6a81db362/bpf/generictracer/k_tracer.c#L370-L394

On CPU mismatch, `fallback_buf `is used but size is still set to `m_buf->real_size` (up to 8KB) and passed downstream.

https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/032473449b53d9f02ec4619d4f5b84e6a81db362/bpf/generictracer/protocol_http.h#L412-L441

`bytes_len (from m_buf->real_size)` is used to read payload data from `u_buf`; if `u_buf` is the 256B fallback, this can over-read and leak memory into telemetry.

https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/032473449b53d9f02ec4619d4f5b84e6a81db362/bpf/tpinjector/tpinjector.c#L192-L206

`real_size `is set up to 8192 bytes and stored with `cpu_id`; `fallback_buf `only contains 256 bytes.

### PoC

Local testing with an AddressSanitizer user-space PoC reproduced the same class of size-mismatch over-read as the vulnerable fallback-buffer path. That result is sufficient to ground the advisory in a fresh local reproduction even though the exact end-to-end eBPF path still depends on host BPF capabilities.

To reproduce the validated behavior locally:

1. create a struct that models `fallback_buf[256]` and `real_size`
2. populate only the 256-byte fallback buffer
3. simulate the CPU mismatch path by using the fallback buffer as the source pointer while preserving a much larger `real_size`
4. perform a read of `real_size` bytes from that 256-byte backing store under ASan

An equivalent reproducer is:

```c
// save as /tmp/poc_msgbuf_oob.c
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct msg_buffer {
  unsigned char fallback_buf[256];
  uint16_t pos;
  uint16_t real_size;
  uint32_t cpu_id;
};

int main(void) {
  struct msg_buffer m = {0};
  unsigned char sink[8192];

  memset(m.fallback_buf, 'A', sizeof(m.fallback_buf));
  m.real_size = 4096;

  memcpy(sink, m.fallback_buf, m.real_size);
  printf("copied %u bytes from a 256-byte fallback buffer\n", m.real_size);
  return 0;
}
```

Compile and run with ASan:

```bash
cc -fsanitize=address -O1 -g -o /tmp/poc_msgbuf_oob /tmp/poc_msgbuf_oob.c
ASAN_OPTIONS=abort_on_error=1 /tmp/poc_msgbuf_oob
```

Expected result:

```text
AddressSanitizer: heap-buffer-overflow or stack-buffer-overflow
```

That user-space PoC matches the size-mismatch condition in the vulnerable code path, even though the exact end-to-end eBPF runtime path still requires host BPF attach/load capability.

### Impact

This is a confidentiality issue in the HTTP tracing path. The vulnerable read occurs in OBI's local fallback-buffer handling when context propagation is enabled, the `tpinjector` sock_msg path is active, HTTP large-buffer capture is configured with a non-zero size, and a CPU mismatch occurs between producer and consumer contexts. Under those conditions, OBI can over-read from the fallback buffer and export unrelated memory through telemetry.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-r6c9-g6q5-qrf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45681
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
