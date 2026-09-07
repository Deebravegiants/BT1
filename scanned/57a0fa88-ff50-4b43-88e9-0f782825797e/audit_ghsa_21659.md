# [H] Exposure of server configuration in github.com/go-vela/server

## Summary
Severity: High
Advisory: GHSA-gv2h-gf8m-r68j
CVE: CVE-2020-26294
CWE: CWE-200, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-gv2h-gf8m-r68j
Type: github-advisory

## Affected
- Go: `github.com/go-vela/compiler` — affected >=0 <0.6.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

* The ability to expose configuration set in the [Vela server](https://github.com/go-vela/server) via [pipeline template functionality](https://go-vela.github.io/docs/templates/overview/).
* It impacts all users of Vela.


Sample of template exposing server configuration [using Sprig's `env` function](http://masterminds.github.io/sprig/os.html):

```yaml
metadata:
  template: true

steps:
  - name: sample
    image: alpine:latest
    commands:
      # OAuth client ID for Vela <-> GitHub communication
      - echo {{ env "VELA_SOURCE_CLIENT" }}
      # secret used for server <-> worker communication
      - echo {{ env "VELA_SECRET" }}
```

### Patches
_Has the problem been patched? What versions should users upgrade to?_

* Upgrade to `0.6.1`

#### Additional Recommended Action(s)

* Rotate all secrets

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

* No

### For more information

If you have any questions or comments about this advisory:

* Email us at [vela@target.com](mailto:vela@target.com)

## References
- https://github.com/go-vela/compiler/security/advisories/GHSA-gv2h-gf8m-r68j
- https://nvd.nist.gov/vuln/detail/CVE-2020-26294
- https://github.com/go-vela/compiler/commit/f1ace5f8a05c95c4d02264556e38a959ee2d9bda
- https://github.com/helm/helm/blob/6297c021cbda1483d8c08a8ec6f4a99e38be7302/pkg/engine/funcs.go#L46-L47
- https://pkg.go.dev/github.com/go-vela/compiler/compiler
