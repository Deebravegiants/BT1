# [M] opentelemetry-collector-contrib: githubreceiver silently ignores configured required_headers authentication

## Summary
Severity: Medium
Advisory: GHSA-w5cv-pw74-4rxc
CVE: CVE-2026-55701
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-w5cv-pw74-4rxc
Type: github-advisory

## Affected
- Go: `github.com/open-telemetry/opentelemetry-collector-contrib/receiver/githubreceiver` — affected >=0 <0.151.0

## Details
## githubreceiver Silently Ignores Configured required_headers Authentication

### Summary

The githubreceiver webhook handler does not enforce the `required_headers` configuration. Headers are validated at startup (config rejects empty keys/values) but never checked on incoming requests. This follows the same pattern as [GHSA-prf6-xjxh-p698](https://github.com/open-telemetry/opentelemetry-collector-contrib/security/advisories/GHSA-prf6-xjxh-p698) (awsfirehosereceiver auth bypass). Verified against current main.

### Details

In `receiver/githubreceiver/config.go`, the `RequiredHeaders` field is defined (line 45) and validated at startup (lines 93-101). But `receiver/githubreceiver/trace_receiver.go` in `handleReq()` (lines 131-185) never references `RequiredHeaders`.

The gitlabreceiver enforces the same config correctly at `receiver/gitlabreceiver/traces_receiver.go:266-270`:

    for key, value := range gtr.cfg.WebHook.RequiredHeaders {
        if r.Header.Get(key) != string(value) {
            return "", fmt.Errorf("%w: %s", errInvalidHeader, key)
        }
    }

### Amplifying factor

The `Secret` field defaults to empty and has no validation requiring it to be set. With an empty secret, `github.ValidatePayload` skips HMAC validation entirely. An operator who configures `required_headers` as their authentication mechanism (without setting `secret`) has zero authentication on the webhook endpoint.

### Impact

An attacker can send arbitrary webhook payloads to the githubreceiver endpoint, bypassing the operator configured authentication. This allows injecting fake CI/CD trace data into the observability pipeline.

### Suggested Fix

Add RequiredHeaders enforcement to `handleReq()`, matching the gitlabreceiver pattern.

## References
- https://github.com/open-telemetry/opentelemetry-collector-contrib/security/advisories/GHSA-w5cv-pw74-4rxc
- https://github.com/open-telemetry/opentelemetry-collector-contrib
