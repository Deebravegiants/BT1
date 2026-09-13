# [M] Argo Server TLS requests could be forged by attacker with network access

## Summary
Severity: Medium
Advisory: GHSA-6c73-2v8x-qpvm
Ecosystem: Go
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-6c73-2v8x-qpvm
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.0.0 <3.0.9
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.1.0 <3.1.6

## Details
### Impact

We are not aware of any exploits. This is a pro-active fix.

Impacted: 

* You are running Argo Server < v3.0 with `--secure=true` or >= v3.0 with `--secure` unspecified (note - running in secure mode is recommended regardless).
* The attacker is within your network. If you expose Argo Server to the Internet then "your network" is "the Internet". 

The Argo Server's keys are packaged within the image. They could be extracted and used to decrypt traffic, or forge requests.

### Patches

https://github.com/argoproj/argo-workflows/pull/6540

### Workarounds

* Make sure that your Argo Server service or pod are not directly accessible outside of your cluster. Put TLS load balancer in front of it.

This was identified by engineers at Jetstack.io

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-6c73-2v8x-qpvm
