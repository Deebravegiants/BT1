# [M] opentelemetry-ebpf-profiler: Unprivileged process can trigger a denial of service on the ebpf-profiler agent

## Summary
Severity: Medium
Advisory: GHSA-f2r5-5m7w-p5cx
CVE: CVE-2026-48496
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-f2r5-5m7w-p5cx
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/ebpf-profiler` — affected >=0.0.202527 <0.0.202622

## Details
### Summary

An unprivileged process can easily trigger the `processPIDEvents` goroutine to be blocked indefinitely, preventing the goroutine from analyzing any new ELF file. The goroutine stays blocked in the `openat2` syscall forever and the profiler can no longer work properly, it is a denial of service.

### Impact

The impact is limited to denial-of-service on the ebpf-profiler agent:
- There has to be a malicious workload albeit unprivileged.
- No exfiltration of data. No loss of data.

###  Fix

Fixed in https://github.com/open-telemetry/opentelemetry-ebpf-profiler/commit/234b685cab31c2cb2f79e966caeab168bcc489e4.

Fix is part of [v.0.0.202622](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/releases/tag/v0.0.202622).

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-profiler/security/advisories/GHSA-f2r5-5m7w-p5cx
- https://github.com/open-telemetry/opentelemetry-ebpf-profiler/commit/234b685cab31c2cb2f79e966caeab168bcc489e4
- https://github.com/open-telemetry/opentelemetry-ebpf-profiler
- https://github.com/open-telemetry/opentelemetry-ebpf-profiler/releases/tag/v0.0.202622
