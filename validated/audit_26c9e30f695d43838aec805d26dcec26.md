### Title
Encryption passwords for key import/export sent as URL query-string parameters instead of request body - ([File: core/cmd/keys_commands.go])

### Summary
Chainlink's key-management CLI commands (regular keys, VRF, OCR, OCR2, P2P) send the new/old keystore encryption password as a URL query parameter (`?newpassword=...` / `?oldpassword=...`) on the authenticated HTTP API instead of passing it in the request body or a header. This mirrors the bug class in CVE-2020-1753 (Ansible k8s module leaking `password`/`token` values by passing them through an insecure, log-visible channel instead of a proper secured input mechanism).

### Finding Description
`ExportKey` and `ImportKey` in `core/cmd/keys_commands.go` build the request URL by concatenating the plaintext password directly into the query string: [1](#0-0) 
The same pattern repeats for VRF keys in `ExportVRFKey`/`ImportVRFKey`: [2](#0-1) 
and is duplicated across `core/cmd/ocr_keys_commands.go`, `core/cmd/ocr2_keys_commands.go`, and `core/cmd/p2p_keys_commands.go` (confirmed via matches for `newpassword=`/`oldpassword=`).

On the server side, `core/web/router.go` is aware that passwords leak via query parameters — it implements a `redact()`/`isBlacklisted()` helper specifically to scrub any query key containing `password` before Chainlink's *own* application logs are written: [3](#0-2) 
This proves the maintainers recognize the sensitivity of these values, but the mitigation only covers Chainlink's internal logging layer. It does not, and cannot, prevent the password from being recorded by anything sitting outside the Go process that has visibility into the full request line/URI — reverse proxies, load balancers, API gateways, TLS-terminating ingress, browser history/autocomplete, HTTP client debug/proxy logs, or `Referer` headers on any subsequent cross-origin navigation. This is exactly the class of exposure CVE-2020-1753 describes: sensitive parameters transiting a channel that is logged/visible outside the application's own redaction/`no_log` controls.

### Impact Explanation
If any infrastructure component between the CLI and the Chainlink node logs full request URLs (a very common default, e.g. standard nginx/ALB/API gateway access logs), the keystore encryption password used to import/export EVM, Solana, VRF, OCR, OCR2, or P2P keys is captured in plaintext in those logs. Anyone with read access to that log store (which may have weaker access controls than the node's own admin session) obtains the password used to decrypt/re-encrypt the exported key file. Combined with the exported/imported key material, this can lead to full compromise of the node's signing keys and impersonation of the node in job runs.

### Likelihood Explanation
Exploitation requires no application-level authentication bypass — it simply requires visibility into infrastructure-level access logs or browser history, which is a common secondary exposure surface in production deployments (shared proxy fleets, aggregated log pipelines, SIEM ingestion), making this a realistic secondary-actor threat even though it does not require action from an unprivileged attacker against the API directly.

### Recommendation
Move `oldpassword`/`newpassword` (and any other CLI-supplied secrets currently built into query strings) into the HTTP request body (already used for the key JSON payload) or into a dedicated header, and update the corresponding server-side handlers to read from there instead of `c.Query(...)`. Audit `core/cmd/keys_commands.go`, `core/cmd/vrf_keys_commands.go`, `core/cmd/ocr_keys_commands.go`, `core/cmd/ocr2_keys_commands.go`, and `core/cmd/p2p_keys_commands.go` for all similar occurrences.

### Proof of Concept
1. Deploy chainlink node behind a reverse proxy/load balancer with default access logging enabled (logs full request URI, a common default configuration).
2. Run `chainlink keys eth export <id> --new-password pwfile --output key.json` (or the VRF/OCR/OCR2/P2P equivalents).
3. The CLI issues `POST /v2/keys/eth/export/<id>?newpassword=<PLAINTEXT>` (`core/cmd/keys_commands.go` `ExportKey`) — the proxy's access log now contains the plaintext password in the URI, even though Chainlink's own internal `redact()` logic would have scrubbed it.
4. Anyone with read access to the proxy/log aggregation system recovers the encryption password for the exported key file.

### Citations

**File:** core/cmd/keys_commands.go (L191-192)
```go
	normalizedPassword := normalizePassword(string(oldPassword))
	resp, err := cli.HTTP.Post(cli.ctx(), cli.path+"/import?oldpassword="+normalizedPassword, bytes.NewReader(keyJSON))
```

**File:** core/cmd/vrf_keys_commands.go (L156-198)
```go
	normalizedPassword := normalizePassword(string(oldPassword))
	resp, err := s.HTTP.Post(s.ctx(), "/v2/keys/vrf/import?oldpassword="+normalizedPassword, bytes.NewReader(keyJSON))
	if err != nil {
		return s.errorOut(err)
	}
	defer func() {
		if cerr := resp.Body.Close(); cerr != nil {
			err = stderrors.Join(err, cerr)
		}
	}()

	var presenter VRFKeyPresenter
	return s.renderAPIResponse(resp, &presenter, "Imported VRF key")
}

// ExportVRFKey saves encrypted copy of VRF key with given public key to
// requested file path.
func (s *Shell) ExportVRFKey(c *cli.Context) error {
	if !c.Args().Present() {
		return s.errorOut(errors.New("Must pass the ID (compressed public key) of the key to export"))
	}

	newPasswordFile := c.String("new-password")
	if len(newPasswordFile) == 0 {
		return s.errorOut(errors.New("Must specify --new-password/-p flag"))
	}
	newPassword, err := os.ReadFile(newPasswordFile)
	if err != nil {
		return s.errorOut(errors.Wrap(err, "Could not read password file"))
	}

	filepath := c.String("output")
	if len(filepath) == 0 {
		return s.errorOut(errors.New("Must specify --output/-o flag"))
	}

	pk, err := getPublicKey(c)
	if err != nil {
		return s.errorOut(err)
	}

	normalizedPassword := normalizePassword(string(newPassword))
	resp, err := s.HTTP.Post(s.ctx(), "/v2/keys/vrf/export/"+pk.String()+"?newpassword="+normalizedPassword, nil)
```

**File:** core/web/router.go (L631-658)
```go
func redact(values url.Values) string {
	cleaned := url.Values{}
	for k, v := range values {
		if isBlacklisted(k) {
			cleaned[k] = []string{"REDACTED"}
			continue
		}
		cleaned[k] = v
	}
	return cleaned.Encode()
}

// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```
