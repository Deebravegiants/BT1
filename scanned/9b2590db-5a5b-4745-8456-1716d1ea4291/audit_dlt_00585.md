# [?] Fix race condition for RW operation of REST handler host (#17092)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-07-06
Source: https://github.com/OffchainLabs/prysm/commit/5547f6456fc1a7835795e4668139617c2a9c4d01
Type: security-commit

## Details
Fix race condition for RW operation of REST handler host (#17092)

**What type of PR is this?**

> Bug fix

**What does this PR do? Why is it needed?**

Make RW operation of REST handler atomic. This can happen when switching
host in fallback scenario.

**Which issue(s) does this PR fix?**

N/A

**Other notes for review**

Running race test like:

```bash
go test -race ./api/rest -run TestHandler_ConcurrentHostSwitch -count=100
```

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

## Patch
### api/rest/rest_handler.go
```diff
@@ -9,6 +9,7 @@ import (
 	"net/http"
 	"os"
 	"strings"
+	"sync/atomic"
 
 	"github.com/OffchainLabs/prysm/v7/api"
 	"github.com/OffchainLabs/prysm/v7/api/apiutil"
@@ -33,16 +34,16 @@ type Handler interface {
 
 type handler struct {
 	client       http.Client
-	host         string
+	host         atomic.Value
 	reqOverrides []reqOption
 }
 
 // newHandler returns a *handler for internal use within the rest package.
 func newHandler(client http.Client, host string) *handler {
 	rh := &handler{
 		client: client,
-		host:   host,
 	}
+	rh.host.Store(host)
 	rh.appendAcceptOverride()
 	return rh
 }
@@ -51,8 +52,8 @@ func newHandler(client http.Client, host string) *handler {
 func NewHandler(client http.Client, host string) Handler {
 	rh := &handler{
 		client: client,
-		host:   host,
 	}
+	rh.host.Store(host)
 	rh.appendAcceptOverride()
 	return rh
 }
@@ -75,13 +76,14 @@ func (c *handler) HttpClient() *http.Client {
 
 // Host returns the underlying HTTP host
 func (c *handler) Host() string {
-	return c.host
+	host, _ := c.host.Load().(string)
+	return host
 }
 
 // Get sends a GET request and decodes the response body as a JSON object into the passed in object.
 // If an HTTP error is returned, the body is decoded as a DefaultJsonError JSON object and returned as the first return value.
 func (c *handler) Get(ctx context.Context, endpoint string, resp any) error {
-	url := c.host + endpoint
+	url := c.Host() + endpoint
 	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
 	if err != nil {
 		return errors.Wrapf(err, "failed to create request for endpoint %s", api.RedactEndpoint(url))
@@ -104,7 +106,7 @@ func (c *handler) Get(ctx context.Context, endpoint string, resp any) error {
 // This is useful for endpoints like /eth/v1/node/health that communicate status via HTTP codes
 // (200 = ready, 206 = syncing, 503 = unavailable) rather than response bodies.
 func (c *handler) GetStatusCode(ctx context.Context, endpoint string) (int, error) {
-	url := c.host + endpoint
+	url := c.Host() + endpoint
 	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
 	if err != nil {
 		return 0, errors.Wrapf(err, "failed to create request for endpoint %s", api.RedactEndpoint(url))
@@ -123,7 +125,7 @@ func (c *handler) GetStatusCode(ctx context.Context, endpoint string) (int, erro
 }
 
 func (c *handler) GetSSZ(ctx context.Context, endpoint string) ([]byte, http.Header, error) {
-	url := c.host + endpoint
+	url := c.Host() + endpoint
 	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
 	if err != nil {
 		return nil, nil, errors.Wrapf(err, "failed to create request for endpoint %s", api.RedactEndpoint(url))
@@ -190,7 +192,7 @@ func (c *handler) Post(
 		return errors.New("data is nil")
 	}
 
-	url := c.host + apiEndpoint
+	url := c.Host() + apiEndpoint
 	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, data)
 	if err != nil {
 		return errors.Wrapf(err, "failed to create request for endpoint %s", api.RedactEndpoint(url))
@@ -224,7 +226,7 @@ func (c *handler) PostSSZ(
 	if data == nil {
 		return nil, nil, errors.New("data is nil")
 	}
-	url := c.host + apiEndpoint
+	url := c.Host() + apiEndpoint
 	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, data)
 	if err != nil {
 		return nil, nil, errors.Wrapf(err, "failed to create request for endpoint %s", api.RedactEndpoint(url))
@@ -319,5 +321,5 @@ func decodeResp(httpResp *http.Response, resp any) error {
 }
 
 func (c *handler) SwitchHost(host string) {
-	c.host = host
+	c.host.Store(host)
 }
```

### api/rest/rest_handler_test.go
```diff
@@ -7,6 +7,7 @@ import (
 	"net/http"
 	"net/http/httptest"
 	"strings"
+	"sync"
 	"testing"
 
 	"github.com/OffchainLabs/prysm/v7/api"
@@ -78,3 +79,41 @@ func TestPostSSZ_JSONErrorBodyIsDecoded(t *testing.T) {
 	require.Equal(t, http.StatusBadRequest, errJson.Code)
 	require.Equal(t, "bad request", errJson.Message)
 }
+
+func TestHandler_ConcurrentHostSwitch(t *testing.T) {
+	newServer := func() *httptest.Server {
+		return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
+			w.Header().Set("Content-Type", api.JsonMediaType)
+			_, _ = w.Write([]byte(`{"data":"ok"}`))
+		}))
+	}
+	srv1 := newServer()
+	defer srv1.Close()
+	srv2 := newServer()
+	defer srv2.Close()
+
+	c := newHandler(http.Client{}, srv1.URL)
+	errs := make(chan error, 100)
+	var wg sync.WaitGroup
+	for range 10 {
+		wg.Go(func() {
+			for range 10 {
+				var resp struct {
+					Data string `json:"data"`
+				}
+				if err := c.Get(context.Background(), "/eth/v1/test", &resp); err != nil {
+					errs <- err
+				}
+			}
+		})
+	}
+	for range 100 {
+		c.SwitchHost(srv2.URL)
+		c.SwitchHost(srv1.URL)
+	}
+	wg.Wait()
+	close(errs)
+	for err := range errs {
+		require.NoError(t, err)
+	}
+}
```

### changelog/syjn99_fix-race-free-rest-host.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fix race condition for reading `host` in REST `handler`.
```
