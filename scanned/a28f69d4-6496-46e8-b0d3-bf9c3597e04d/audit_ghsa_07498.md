# [M] Capsule: CapsuleConfiguration NodeMetadata regex fields lack webhook validation, allowing MustCompile panic on all Node admission requests

## Summary
Severity: Medium
Advisory: GHSA-68cj-mvg9-rgm2
CVE: CVE-2026-65834
CWE: CWE-20, CWE-248
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-68cj-mvg9-rgm2
Type: github-advisory

## Affected
- Go: `github.com/projectcapsule/capsule` — affected >=0 <0.13.8

## Details
### Summary

`CapsuleConfiguration.Spec.NodeMetadata.ForbiddenLabels.Regex` and `ForbiddenAnnotations.Regex` are never validated by any admission webhook. A Cluster Admin can persist a malformed regex to etcd without being blocked. Once stored, every Node `CREATE`, `UPDATE`, or `PATCH` request triggers `regexp.MustCompile()` in `pkg/api/forbidden_list.go:36`, which **panics** and crashes the node admission webhook — causing a cluster-wide Denial of Service for all Node operations.

### Root cause

`internal/webhook/tenant/validation/` contains dedicated regex validators for every Tenant regex field (hostname, storageclass, ingressclass, containerregistry, etc.). `internal/webhook/cfg/` contains **no regex validator at all** — only `owners.go`, `serviceaccount.go`, and `warnings.go`.

The downstream consumer `internal/webhook/node/user_metadata.go` calls:
```go
// line 131
matched = forbiddenLabels.RegexMatch(label)
// line 150
matched = forbiddenAnnotations.RegexMatch(annotation)
```

Which routes to `pkg/api/forbidden_list.go:36`:
```go
func (in ForbiddenListSpec) RegexMatch(value string) (ok bool) {
    if len(in.Regex) > 0 {
        ok = regexp.MustCompile(in.Regex).MatchString(value) // ← panics on invalid regex
    }
    return ok
}
```

Unlike `regexp.Compile`, `regexp.MustCompile` panics instead of returning an error. Since no webhook validates the `CapsuleConfiguration` regex fields before storage, a malformed value reaches `MustCompile` on every Node admission request.

### Comparison with existing CVEs

`GHSA-f94q-w3w8-cj67` and `GHSA-gxjc-74v5-3vx3` affect individual Tenant fields — their validators existed but checked the wrong field. This issue is different: **no validator exists at all** for `CapsuleConfiguration` regex fields, and the blast radius is cluster-wide (all Nodes), not scoped to one tenant.

### PoC

```go
package main

import (
    "fmt"
    "regexp"
)

type ForbiddenListSpec struct{ Regex string }

// Exact copy of pkg/api/forbidden_list.go:34-38
func (in ForbiddenListSpec) RegexMatch(value string) bool {
    if len(in.Regex) > 0 {
        return regexp.MustCompile(in.Regex).MatchString(value)
    }
    return false
}

func main() {
    // 1. cfg webhook has no validator → invalid regex stored in etcd
    // (no webhook in internal/webhook/cfg/ checks regex fields)

    // 2. Stored malformed regex loaded from CapsuleConfiguration
    forbidden := ForbiddenListSpec{Regex: `[invalid-regex(`}

    // 3. node/user_metadata.go:131 called on every Node admission request
    defer func() {
        if r := recover(); r != nil {
            fmt.Printf("PANIC: %v\n", r)
            // Output: PANIC: regexp: Compile(`[invalid-regex(`): error parsing regexp: missing closing ]
        }
    }()
    forbidden.RegexMatch("kubernetes.io/hostname")
}
```

Expected output:
```
PANIC: regexp: Compile(`[invalid-regex(`): error parsing regexp: missing closing ]: `[invalid-regex(`
```

### Fix
 Add a `node_metadata_regex.go` handler to `internal/webhook/cfg/` following the same pattern as `forbidden_annotations_regex.go`:

  ```go
  package cfg

  import (
      "context"
      "regexp"

      "sigs.k8s.io/controller-runtime/pkg/client"
      "sigs.k8s.io/controller-runtime/pkg/webhook/admission"

      capsulev1beta2 "github.com/projectcapsule/capsule/api/v1beta2"
      ad "github.com/projectcapsule/capsule/pkg/runtime/admission"
      "github.com/projectcapsule/capsule/pkg/runtime/events"
      "github.com/projectcapsule/capsule/pkg/runtime/handlers"
  )

  type nodeMetadataRegexHandler struct{}

  func NodeMetadataRegexHandler() handlers.TypedHandler[*capsulev1beta2.CapsuleConfiguration] {
      return &nodeMetadataRegexHandler{}
  }

  func (h *nodeMetadataRegexHandler) OnCreate(
      _ client.Client,
      _ client.Reader,
      cfg *capsulev1beta2.CapsuleConfiguration,
      _ admission.Decoder,
      _ events.EventRecorder,
  ) handlers.Func {
      return func(_ context.Context, req admission.Request) *admission.Response {
          return h.validate(cfg, req)
      }
  }

  func (h *nodeMetadataRegexHandler) OnDelete(
      client.Client,
      client.Reader,
      *capsulev1beta2.CapsuleConfiguration,
      admission.Decoder,
      events.EventRecorder,
  ) handlers.Func {
      return func(context.Context, admission.Request) *admission.Response {
          return nil
      }
  }

  func (h *nodeMetadataRegexHandler) OnUpdate(
      _ client.Client,
      _ client.Reader,
      cfg *capsulev1beta2.CapsuleConfiguration,
      _ *capsulev1beta2.CapsuleConfiguration,
      _ admission.Decoder,
      _ events.EventRecorder,
  ) handlers.Func {
      return func(_ context.Context, req admission.Request) *admission.Response {
          return h.validate(cfg, req)
      }
  }

  func (h *nodeMetadataRegexHandler) validate(cfg *capsulev1beta2.CapsuleConfiguration, req admission.Request) *admission.Response {
      if cfg.Spec.NodeMetadata == nil {
          return nil
      }

      expressions := map[string]string{
          "labels":      cfg.Spec.NodeMetadata.ForbiddenLabels.Regex,
          "annotations": cfg.Spec.NodeMetadata.ForbiddenAnnotations.Regex,
      }

      for scope, expression := range expressions {
          if expression == "" {
              continue
          }

          if _, err := regexp.Compile(expression); err != nil {
              return ad.Denyf(
                  "unable to compile regex %q for forbidden %s: %v",
                  expression,
                  scope,
                  err,
              )
          }
      }

      return nil
  }

```
```
  Step 2: Register the handler in cmd/controller/main.go:

  route.ConfigValidation(
      cfgvalidation.Handler(cfg,
          cfgvalidation.WarningHandler(),
          cfgvalidation.ServiceAccountHandler(),
          cfgvalidation.OwnerHandler(),
          cfgvalidation.NodeMetadataRegexHandler(), // ← ADD THIS LINE
      ),
  ),
```


### Impact

 A Cluster Admin (or compromised admin account) can update CapsuleConfiguration
  with a malformed NodeMetadata regex (e.g., `[invalid-regex(`). The update is
  accepted without validation and persisted to etcd. Once stored, every subsequent
  Node admission request triggers `regexp.MustCompile()` with the invalid pattern,
  causing the Capsule node webhook to panic.

  **Affected operations (cluster-wide):**
  - Node labeling, annotations, and taints (`kubectl label/annotate/taint node`)
  - Cluster autoscaler operations (cannot register or remove nodes)
  - Cloud provider node lifecycle management (metadata sync, status updates)
  - Node maintenance workflows (cordon, drain, uncordon)

  **Severity:**
  This is a **cluster-wide Denial of Service** affecting all Node infrastructure
  operations. Unlike tenant-scoped CVEs (GHSA-f94q-w3w8-cj67, GHSA-gxjc-74v5-3vx3)
  that impact only Ingress or Namespace operations within a single tenant, this
  vulnerability blocks the entire cluster's ability to manage nodes.

  The cluster cannot scale, perform maintenance, or process any node metadata
  changes until a Cluster Admin manually corrects the CapsuleConfiguration—requiring
  direct kubectl access with valid YAML.

## References
- https://github.com/projectcapsule/capsule/security/advisories/GHSA-68cj-mvg9-rgm2
- https://nvd.nist.gov/vuln/detail/CVE-2026-65834
- https://github.com/projectcapsule/capsule
- https://github.com/projectcapsule/capsule/releases/tag/v0.13.8
