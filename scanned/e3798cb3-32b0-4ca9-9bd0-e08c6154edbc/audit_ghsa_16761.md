# [H] Minder's GitHub Webhook Handler vulnerable to DoS from un-validated requests

## Summary
Severity: High
Advisory: GHSA-9c5w-9q3f-3hv7
CVE: CVE-2024-34084
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-07
Source: https://github.com/advisories/GHSA-9c5w-9q3f-3hv7
Type: github-advisory

## Affected
- Go: `github.com/stacklok/minder` — affected >=0 <0.0.48

## Details
Minder's `HandleGithubWebhook` is susceptible to a denial of service attack from an untrusted HTTP request. The vulnerability exists before the request has been validated, and as such the request is still untrusted at the point of failure. This allows an attacker with the ability to send requests to `HandleGithubWebhook` to crash the Minder controlplane and deny other users from using it.

One of the first things that `HandleGithubWebhook` does is to validate the payload signature. This is done by way of the internal helper `validatePayloadSignature`:

https://github.com/stacklok/minder/blob/ee66f6c0763212503c898cfefb65ce1450c7f5ac/internal/controlplane/handlers_githubwebhooks.go#L213-L218

`validatePayloadSignature` generates a reader from the incoming request by way of the internal helper `readerFromRequest`:

https://github.com/stacklok/minder/blob/ee66f6c0763212503c898cfefb65ce1450c7f5ac/internal/controlplane/handlers_githubwebhooks.go#L337-L342

To create a reader from the incoming request, `readerFromRequest` first reads the request body entirely into memory on line 368:

https://github.com/stacklok/minder/blob/ee66f6c0763212503c898cfefb65ce1450c7f5ac/internal/controlplane/handlers_githubwebhooks.go#L367-L377

This is a vulnerability, since an HTTP request with a large body can exhaust the memory of the machine running Minder and cause the Go runtime to crash Minder.

Note that this occurs before Minder has validated the request, and as such, the request is still untrusted.

To test this out, we can use the existing `TestHandleWebHookRepository` unit test and modify the HTTP request body to be large. 

To do that, change these lines:

https://github.com/stacklok/minder/blob/ee66f6c0763212503c898cfefb65ce1450c7f5ac/internal/controlplane/handlers_githubwebhooks_test.go#L278-L283

... to these lines:
```go
	packageJson, err := json.Marshal(event)
	require.NoError(t, err, "failed to marshal package event")

        maliciousBody := strings.NewReader(strings.Repeat("1337", 1000000000))
        maliciousBodyReader := io.MultiReader(maliciousBody, maliciousBody, maliciousBody, maliciousBody, maliciousBody)
        _ = packageJson

	client := &http.Client{}
	req, err := http.NewRequest("POST", fmt.Sprintf("http://%s", addr), maliciousBodyReader)
	require.NoError(t, err, "failed to create request")
```

Then run the unit test again. WARNING, SAVE ALL WORK BEFORE DOING THIS.

On my local machine, this causes the machine to freeze, and Go finally performs a sigkill: 

```
signal: killed
FAIL      github.com/stacklok/minder/internal/controlplane          30.759s
FAIL
```

## References
- https://github.com/stacklok/minder/security/advisories/GHSA-9c5w-9q3f-3hv7
- https://nvd.nist.gov/vuln/detail/CVE-2024-34084
- https://github.com/stacklok/minder/commit/3e5a527d2f1b535159206161d1d519602c75bd0d
- https://github.com/stacklok/minder
- https://github.com/stacklok/minder/blob/ee66f6c0763212503c898cfefb65ce1450c7f5ac/internal/controlplane/handlers_githubwebhooks.go#L213-L218
- https://github.com/stacklok/minder/blob/ee66f6c0763212503c898cfefb65ce1450c7f5ac/internal/controlplane/handlers_githubwebhooks.go#L337-L342
- https://github.com/stacklok/minder/blob/ee66f6c0763212503c898cfefb65ce1450c7f5ac/internal/controlplane/handlers_githubwebhooks.go#L367-L377
- https://github.com/stacklok/minder/blob/ee66f6c0763212503c898cfefb65ce1450c7f5ac/internal/controlplane/handlers_githubwebhooks_test.go#L278-L283
