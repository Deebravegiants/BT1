# [M] Stacklok Minder vulnerable to denial of service from maliciously crafted templates

## Summary
Severity: Medium
Advisory: GHSA-crgc-2583-rw27
CVE: CVE-2024-35194
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-crgc-2583-rw27
Type: github-advisory

## Affected
- Go: `github.com/stacklok/minder` — affected >=0 <0.0.50

## Details
Minder engine is susceptible to a denial of service from memory exhaustion that can be triggered from maliciously created templates.

Minder engine uses templating to generate strings for various use cases such as URLs, messages for pull requests, descriptions for advisories. In some cases can the user control both the template and the params for it, and in a subset of these cases, Minder reads the generated template entirely into memory. When Minders templating meets both of these conditions, an attacker is able to generate large enough templates that Minder will exhaust memory and crash.

One of these places is the REST ingester:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L115-L123

With control over both endpoint and `retp` on the following line:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L121

… an attacker can make Minder generate a large template that Minder reads into memory on the following line by invoking `endpoint.String()`:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L131

Consider this example:

```go
package main

import (
        "fmt"
        "html/template"
        "os"
)

type EndpointTemplateParams struct {
        // Params are the parameters to be used in the template
        Params map[string]any
}

func main() {
        retp := &EndpointTemplateParams{
                Params: map[string]any{
                        "params": make([]string, 10),
                },
        }
        fmt.Println(retp)
        const templ = `
        {{range $idx, $e := .Params.params}}
    loooooooooooooooooooooooooooooooong-string-{{$idx}}
{{end}}
        {{range $idx, $e := .Params.params}}
    loooooooooooooooooooooooooooooooong-string-{{$idx}}
{{end}}
        {{range $idx, $e := .Params.params}}
    loooooooooooooooooooooooooooooooong-string-{{$idx}}
{{end}}`
        tmpl := template.Must(template.New("").Parse(templ))
        if err := tmpl.Execute(os.Stdout, retp); err != nil {
                panic(err)
        }
}

```

This example imitates the behavior on these lines:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L115-L123

Running this example generates the following template:

```
    loooooooooooooooooooooooooooooooong-string-0

    loooooooooooooooooooooooooooooooong-string-1

    loooooooooooooooooooooooooooooooong-string-2

    loooooooooooooooooooooooooooooooong-string-3

    loooooooooooooooooooooooooooooooong-string-4

    loooooooooooooooooooooooooooooooong-string-5

    loooooooooooooooooooooooooooooooong-string-6

    loooooooooooooooooooooooooooooooong-string-7

    loooooooooooooooooooooooooooooooong-string-8

    loooooooooooooooooooooooooooooooong-string-9


    loooooooooooooooooooooooooooooooong-string-0

    loooooooooooooooooooooooooooooooong-string-1

    loooooooooooooooooooooooooooooooong-string-2

    loooooooooooooooooooooooooooooooong-string-3

    loooooooooooooooooooooooooooooooong-string-4

    loooooooooooooooooooooooooooooooong-string-5

    loooooooooooooooooooooooooooooooong-string-6

    loooooooooooooooooooooooooooooooong-string-7

    loooooooooooooooooooooooooooooooong-string-8

    loooooooooooooooooooooooooooooooong-string-9


    loooooooooooooooooooooooooooooooong-string-0

    loooooooooooooooooooooooooooooooong-string-1

    loooooooooooooooooooooooooooooooong-string-2

    loooooooooooooooooooooooooooooooong-string-3

    loooooooooooooooooooooooooooooooong-string-4

    loooooooooooooooooooooooooooooooong-string-5

    loooooooooooooooooooooooooooooooong-string-6

    loooooooooooooooooooooooooooooooong-string-7

    loooooooooooooooooooooooooooooooong-string-8

    loooooooooooooooooooooooooooooooong-string-9
```

A malicious user can call the loop more times, increase the loop count and/or make the repeated long string longer to make the size of the template bigger.

A sufficiently large template will consume a lot of memory on this line which will exhaust memory on the machine and crash the Minder server:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L121

Minder should enforce a limit to generated templates before reading them into memory.

The following templates are believed to be vulnerable:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L121

https://github.com/stacklok/minder/blob/e7f9914de9af5a69e3e6fe2bdfaaf22e62be42c0/internal/engine/actions/remediate/pull_request/pull_request.go#L199

https://github.com/stacklok/minder/blob/e7f9914de9af5a69e3e6fe2bdfaaf22e62be42c0/internal/engine/actions/remediate/pull_request/pull_request.go#L510

Minder has a few other templates especially in its engine which needs reviewing too. As a default, all templates should be limited in size before Minder reads them into memory.

## References
- https://github.com/stacklok/minder/security/advisories/GHSA-crgc-2583-rw27
- https://nvd.nist.gov/vuln/detail/CVE-2024-35194
- https://github.com/stacklok/minder/commit/fe321d345b4f738de6a06b13207addc72b59f892
- https://github.com/stacklok/minder
