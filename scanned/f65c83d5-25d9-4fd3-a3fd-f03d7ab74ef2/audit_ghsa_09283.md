# [M] OpenTelemetry eBPF Instrumentation: Unbounded BPF internal metrics replay can exhaust CPU

## Summary
Severity: Medium
Advisory: GHSA-89c6-vpcj-7vj4
CVE: CVE-2026-45680
CWE: CWE-400, CWE-834
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-89c6-vpcj-7vj4
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0 <0.9.0

## Details
### Summary

OBI replays BPF probe hits into histogram observations by looping once per recorded run count. On busy systems, the run-count delta can become very large, causing the metrics exporter to spend excessive CPU time in a tight loop every collection interval.

### Details

The vulnerable loop is in [pkg/export/prom/prom_bpf.go](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/4a39d3b307968df4b54e89b8dee297e7d772ca29/pkg/export/prom/prom_bpf.go#L128-L144). During each metrics tick, OBI iterates through `probeMetrics` and then executes `for range metric.count`, invoking `BpfProbeLatency(...)` for each individual recorded hit.

The count comes from [`calculateStats()`](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/4a39d3b307968df4b54e89b8dee297e7d772ca29/pkg/export/prom/prom_bpf.go#L326-L335) in the same file, where `deltaCount := bp.runCount - bp.prevRunCount` is calculated and returned without any cap before the per-hit replay loop.

If probe activity spikes between scrape intervals, `deltaCount` can be very large. The exporter then spends CPU time proportional to the number of probe hits rather than the number of metric series.

### PoC

Local testing with a small reproducer confirmed the replay-loop behavior and showed CPU scaling with the recorded hit count rather than the number of metric series.

Use a vulnerable build and enable internal metrics export:

```bash
git checkout v0.0.0-rc.1+build
make build
export OTEL_EBPF_INTERNAL_METRICS_PROMETHEUS_PORT=9090
sudo ./bin/obi
```

Create a high-rate workload that repeatedly exercises traced probes. For example, generate HTTP traffic against an instrumented service:

```bash
python3 -m http.server 18081
```

Then drive it:

```bash
seq 1 500000 | xargs -P 128 -I{} curl -s http://127.0.0.1:18081 >/dev/null
```

At the same time, scrape metrics repeatedly:

```bash
while true; do curl -s http://127.0.0.1:9090/metrics >/dev/null; done
```

On a vulnerable build, OBI CPU consumption rises sharply during the metrics loop because histogram updates are replayed once per counted probe execution. The effect is visible in `top` or `pidstat` and is most pronounced under sustained high request volume.

### Impact

This is an availability issue in the internal metrics path. Any deployment that enables BPF internal metrics and traces busy workloads is affected. Attackers can indirectly consume CPU in the privileged agent by driving enough activity through instrumented services.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-89c6-vpcj-7vj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-45680
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
