# [M] free5gc UDR fail-open request handling in PolicyDataSubsToNotifySubsIdPut may allow unintended subscription updates after input errors

## Summary
Severity: Medium
Advisory: GHSA-gx38-8h33-pmxr
CVE: CVE-2026-40249
CWE: CWE-636, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-gx38-8h33-pmxr
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udr` — affected >=0

## Details
### Summary
A fail-open request handling flaw in the UDR service causes the `/nudr-dr/v2/policy-data/subs-to-notify/{subsId}` PUT handler to continue processing requests even after request body retrieval or deserialization errors.

This may allow unintended modification of existing Policy Data notification subscriptions with invalid, empty, or partially processed input, depending on downstream processor behavior.

### Details
The endpoint `PUT /nudr-dr/v2/policy-data/subs-to-notify/{subsId}` is intended to update an existing Policy Data notification subscription only after the HTTP request body has been successfully read and parsed into a valid `PolicyDataSubscription` object. [file:93]

In the free5GC UDR implementation, the function `HandlePolicyDataSubsToNotifySubsIdPut` in`NFs/udr/internal/sbi/api_datarepository.go` does not terminate execution after input-processing failures. [file:93]

The request flow is:

1. The handler calls `c.GetRawData()` to read the HTTP request body. [file:93]
2. If `GetRawData()` fails, the handler sends an HTTP 500 error response, but **does not return**. [file:93]
3. The handler then calls `openapi.Deserialize(policyDataSubscription, reqBody, "application/json")`. [file:93]
4. If deserialization fails, the handler sends an HTTP 400 error response, but again **does not return**. [file:93]
5. Execution continues and the handler still invokes `s.Processor().PolicyDataSubsToNotifySubsIdPutProcedure(c, subsId, policyDataSubscription)`. [file:93]

As a result, the endpoint operates in a fail-open manner: request processing may continue after fatal input validation or body handling errors, instead of being safely aborted. [file:93]

The issue is compounded by the handler's deserialization call, which passes `policyDataSubscription` directly to `openapi.Deserialize(...)` instead of passing a pointer to the destination object. This inconsistent usage further increases the risk that request processing continues with an empty, partially initialized, or otherwise unintended subscription object. [file:93]

This differs from safer handlers in the same file, which use a helper pattern that explicitly returns on body read or deserialization failure before calling the corresponding processor routine. [file:93]

### Security Impact
This issue affects a write-capable API that updates Policy Data notification subscriptions identified by `subsId`. [file:93]  
Because execution continues after body read or parsing failure, the processor may receive an uninitialized, partially initialized, or otherwise unintended `PolicyDataSubscription` object for persistence. [file:93]

The exact runtime impact depends on downstream processor behavior and storage validation. [file:93]  
At minimum, this is a security-relevant robustness flaw that can lead to inconsistent request handling or unintended modification attempts; under certain runtime conditions it may allow updates that should not be processed after an input error. [file:93]

### Reproduction Status
The code path has been statically confirmed. [file:93]  A complete runtime proof of unintended subscription modification after
`GetRawData()` or deserialization failure has not yet been established. [file:93]

### Patch
The handler should immediately terminate after sending an error response for body read or deserialization failure. [file:93]

A minimal fix is to add missing `return` statements in `HandlePolicyDataSubsToNotifySubsIdPut` and pass a pointer to the destination
object during deserialization: [file:93]

```go
reqBody, err := c.GetRawData()
if err != nil {
    logger.DataRepoLog.Errorf("Get Request Body error: %+v", err)
    pd := openapi.ProblemDetailsSystemFailure(err.Error())
    c.Set(sbi.IN_PB_DETAILS_CTX_STR, pd.Cause)
    c.JSON(http.StatusInternalServerError, pd)
    return
}

err = openapi.Deserialize(&policyDataSubscription, reqBody, "application/json")
if err != nil {
    logger.DataRepoLog.Errorf("Deserialize Request Body error: %+v", err)
    pd := util.ProblemDetailsMalformedReqSyntax(err.Error())
    c.Set(sbi.IN_PB_DETAILS_CTX_STR, pd.Cause)
    c.JSON(http.StatusBadRequest, pd)
    return
}
```

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-gx38-8h33-pmxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-40249
- https://github.com/free5gc/udr
