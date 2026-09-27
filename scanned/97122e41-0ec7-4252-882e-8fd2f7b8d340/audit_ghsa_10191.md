# [H] kyverno apicall servicecall implicit bearer token injection leaks kyverno serviceaccount token

## Summary
Severity: High
Advisory: GHSA-q93q-v844-jrqp
CVE: CVE-2026-40868
CWE: CWE-441, CWE-922
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-q93q-v844-jrqp
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0 <1.17.0

## Details
kyverno’s apiCall servicecall helper implicitly injects `Authorization: Bearer ...` using the kyverno controller serviceaccount token when a policy does not explicitly set an Authorization header. because `context.apiCall.service.url` is policy-controlled, this can send the kyverno serviceaccount token to an attacker-controlled endpoint (confused deputy).

namespaced policies are blocked from servicecall usage by the namespaced `urlPath` gate in `pkg/engine/apicall/apiCall.go`, so this report is scoped to ClusterPolicy and global context usage.

## attacker model

the attacker can create or update a ClusterPolicy (or create a GlobalContextEntry) which uses `context.apiCall.service.url` and can choose the request URL and headers. a cross-boundary framing for real deployments is gitops: if the policy repo/controller is compromised, the ClusterPolicy/global context entry becomes untrusted input to kyverno.

## relevant links

- repository: https://github.com/kyverno/kyverno
- commit: 17aeb52337fd66adb0c8126213ba076612a287a7
- callsite (token injection): https://github.com/kyverno/kyverno/blob/17aeb52337fd66adb0c8126213ba076612a287a7/pkg/engine/apicall/executor.go#L150-L173
- namespaced policy gate (servicecall blocked): https://github.com/kyverno/kyverno/blob/17aeb52337fd66adb0c8126213ba076612a287a7/pkg/engine/apicall/apiCall.go#L67-L83

## root cause

in `(*executor).addHTTPHeaders`, kyverno reads the serviceaccount token from `/var/run/secrets/kubernetes.io/serviceaccount/token` and injects it when the outgoing request has no Authorization header:

```go
if req.Header.Get("Authorization") == "" {
  token := a.getToken()
  if token != "" {
    req.Header.Add("Authorization", "Bearer "+token)
  }
}
```

## proof of concept

the attached `poc.zip` is a reproducible cluster PoC. it uses an in-cluster HTTP receiver which logs the Authorization header it receives. the PoC does not print token bytes; it only checks that the received header is non-empty and not equal to the negative control.

run (one command):

```bash
unzip poc.zip -d poc
cd poc
make test
```

canonical (expected: implicit token injection):

```bash
unzip poc.zip -d poc
cd poc
make canonical
```

expected output includes:

```
[CALLSITE_HIT]: executor.addHTTPHeaders Authorization=="" -> read_serviceaccount_token=true
[PROOF_MARKER]: authorization_header_injected=true token_nonempty=true
```

control (expected: explicit Authorization header disables auto-injection):

```bash
unzip poc.zip -d poc
cd poc
make control
```

expected output includes:

```
[CALLSITE_HIT]: executor.addHTTPHeaders Authorization!="" -> autoinject_skipped=true
[NC_MARKER]: authorization_header_injected=false
```

optional: the canonical run may also print an `[RBAC]: ...` line using `kubectl auth can-i` with the exfiltrated token, to show concrete privileges without exposing the token.

## impact

token exfiltration: the kyverno controller serviceaccount token is sent to a policy-controlled endpoint. impact depends on the rbac bound to that serviceaccount in the target deployment.

## recommended fix

do not auto-inject the kyverno serviceaccount token into policy-controlled servicecall requests. require explicit Authorization configuration, or enforce a strict allowlist of destinations where credentials may be attached and document the behavior.

## workarounds

- avoid using servicecall to arbitrary urls in policies.
- set an explicit Authorization header in servicecall policies to prevent implicit token injection.


[poc.zip](https://github.com/user-attachments/files/25352288/poc.zip)
[PR_DESCRIPTION.md](https://github.com/user-attachments/files/25352289/PR_DESCRIPTION.md)

oleh

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-q93q-v844-jrqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40868
- https://github.com/kyverno/kyverno
