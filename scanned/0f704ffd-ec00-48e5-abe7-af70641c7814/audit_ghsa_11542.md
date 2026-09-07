# [M] Traefik: kubernetes gateway rule injection via unescaped backticks in HTTPRoute match values

## Summary
Severity: Medium
Advisory: GHSA-8q2w-wr49-whqj
CVE: CVE-2026-29777
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-8q2w-wr49-whqj
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.10
- Go: `github.com/traefik/traefik` — affected >=0
- Go: `github.com/traefik/traefik/v2` — affected >=0

## Details
## Summary

There is a potential vulnerability in Traefik's Kubernetes Gateway provider related to rule injection.

A tenant with write access to an HTTPRoute resource can inject backtick-delimited rule tokens into Traefik's router rule language via unsanitized header or query parameter match values. In shared gateway deployments, this can bypass listener hostname constraints and redirect traffic for victim hostnames to attacker-controlled backends.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.6.10

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

hey Traefik,


repo: https://github.com/traefik/traefik
commit: a4a91344edcdd6276c1b766ca19ee3f0e346480f (as-of 2026-03-02)

traefik's kubernetes gateway provider builds router rules by interpolating HTTPRoute match values into the traefik rule language using backtick-delimited string literals (e.g., `Header(`name`,`value`)`, `Query(`name`,`value`)`) without escaping or validation.

because backtick is a delimiter in the rule language, a tenant-controlled backtick can terminate the literal and inject additional rule tokens (for example `) || HostRegexp(`.\*`) || ...`). this changes the parsed ast so that an injected OR branch is not gated by the intended `Host(...)` constraint due to operator precedence, and can result in end-to-end routing hijack (victim host routed to attacker backends).

in shared gateway deployments that rely on gateway API listener hostname constraints to isolate tenants, this can enable cross-tenant routing hijack to attacker-controlled backends.

## expected vs actual

expected: provider-generated rules must be injection-safe; tenant-controlled match values must not be able to change the rule parse tree beyond literal argument content, especially across listener hostname-constraint boundaries in shared gateway deployments.

actual: a backtick inside a header/query match value can inject an OR branch into the generated rule, changing the ast root from `and` to `or` and enabling hostname-constraint bypass.

## severity

HIGH (impact ceiling may reach the top severity tier in shared gateway threat models; end-to-end kubernetes reproduction is recommended to demonstrate cross-tenant routing impact).

CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N = 8.7

cwe: CWE-74 (improper neutralization of special elements in output used by a downstream component)

## affected versions

- confirmed vulnerable at: a4a91344edcdd6276c1b766ca19ee3f0e346480f (pinned commit)
- release matrix: not yet confirmed (needs version mapping for gateway api provider in v3)

## affected code

- `pkg/provider/kubernetes/gateway/httproute.go`: `buildHeaderRules` and `buildQueryParamRules` build `Header(`%s`,`%s`)` / `Query(`%s`,`%s`)` without escaping
- `pkg/provider/kubernetes/gateway/grpcroute.go`: `buildGRPCHeaderRules` builds `Header(`%s`,`%s`)` / `HeaderRegexp(`%s`,`%s`)` without escaping
- `pkg/provider/kubernetes/knative/kubernetes.go`: `buildRule` builds `Header(`%s`,`%s`)` without escaping
- the generated rule string is parsed by `pkg/muxer/http/parser.go` (predicate-based rule parser)
- github permalinks (pinned):
  - https://github.com/traefik/traefik/blob/a4a91344edcdd6276c1b766ca19ee3f0e346480f/pkg/provider/kubernetes/gateway/httproute.go#L742
  - https://github.com/traefik/traefik/blob/a4a91344edcdd6276c1b766ca19ee3f0e346480f/pkg/provider/kubernetes/gateway/httproute.go#L761

## root cause

the kubernetes gateway provider formats rule strings using backticks as string delimiters:

```go
rules = append(rules, fmt.Sprintf("Header(`%s`,`%s`)", header.Name, header.Value))
rules = append(rules, fmt.Sprintf("Query(`%s`,`%s`)", qp.Name, qp.Value))
```

if `header.Value` (or `qp.Value`) contains a backtick and operator tokens, it can terminate the literal and inject additional rule-language tokens, changing the parse tree.

## attacker control

attacker-controlled input is the kubernetes control plane object `HTTPRoute` in a tenant namespace. the attacker controls:

1. `HTTPRoute.Spec.Rules[].Matches[].Headers[].Value` and/or `QueryParams[].Value` (string)
2. the payload content, including backticks and rule tokens

## impact

in shared gateway setups, this can bypass gateway API listener hostname constraints, causing requests for victim hostnames to be routed to attacker backends. downstream effects can include credential/token capture and request forgery, depending on the workload behind the gateway.

traefik's documentation frames gateway API as providing safer multi-tenant primitives via listener constraints (see https://doc.traefik.io/traefik/security/multi-tenant-kubernetes/). rule injection breaks those constraints when they are relied upon as a boundary.

## reproduction (attachment: poc.zip)

attachment includes `poc.zip` with an integration PoC that:

- shows canonical behavior where injection changes the parsed ast root to `or` and routes `victim.com` to the attacker handler (emits `[PROOF_MARKER]`)
- shows a negative control using injection-safe quoting (`%q`) where the ast root remains `and` and routes `victim.com` to the victim handler (emits `[NC_MARKER]`)

run canonical:

```bash
unzip poc.zip -d poc
cd poc
make canonical
```

canonical output excerpt:

```
[CALLSITE_HIT]
[PROOF_MARKER]
```

run control:

```bash
unzip poc.zip -d poc
cd poc
make control
```

control output excerpt:

```
[NC_MARKER]
```

## recommended fix

encode rule arguments using injection-safe quoting (for example `fmt.Sprintf("Header(%q,%q)", name, value)`), or otherwise reject/escape backticks and other rule-language metacharacters before interpolation. add regression tests that include backticks and operator tokens inside header/query match values and assert they cannot change the parse tree.

**fix accepted when:** tenant-controlled HTTPRoute match values cannot inject operators into the generated rule string and cannot change the resulting parsed ast structure.


[[poc.zip](https://github.com/user-attachments/files/25698814/poc.zip)](https://github.com/user-attachments/files/25698814/poc.zip)
[[PR_DESCRIPTION.md](https://github.com/user-attachments/files/25698815/PR_DESCRIPTION.md)](https://github.com/user-attachments/files/25698815/PR_DESCRIPTION.md)
[[attack_scenario.md](https://github.com/user-attachments/files/25698816/attack_scenario.md)](https://github.com/user-attachments/files/25698816/attack_scenario.md)


cheers,
Oleh Konko

</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-8q2w-wr49-whqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-29777
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.6.10
