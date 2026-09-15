# [H] free5gc UDR nudr-dr influenceData/subs-to-notify leaks SUPI in error response body without authentication

## Summary
Severity: High
Advisory: GHSA-wrwh-rpq4-87hf
CVE: CVE-2026-40245
CWE: CWE-200, CWE-202, CWE-209
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-wrwh-rpq4-87hf
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udr` — affected >=0

## Details
### Summary
An information disclosure vulnerability in the UDR service allows any unauthenticated  attacker with access to the 5G Service Based Interface (SBI) to retrieve stored subscriber identifiers (SUPI/IMSI) with a single HTTP GET request requiring no parameters or credentials.

### Details
The endpoint `GET /nudr-dr/v2/application-data/influenceData/subs-to-notify` (defined in 3GPP TS 29.519) requires at least one query parameter (`dnns`, `snssais`,  `supis`, or `internalGroupIds`) to filter results.

In the free5GC UDR implementation, the input validation is present but ineffective because the handler does not return after sending the HTTP 400 error. The request handling flow is:

1. The function `HandleApplicationDataInfluenceDataSubsToNotifyGet` in  `./free5gc_4-2-1/free5gc/NFs/udr/internal/sbi/api_datarepository.go`  (around line 2793) checks whether all of `dnn`, `snssai`, `internalGroupId`, 
   and `supi` are empty.
2. If they are all empty, it builds a `problemDetails` structure and calls `c.JSON(http.StatusBadRequest, problemDetails)` to send a 400 response, **but it does not return afterwards**.
3. Execution continues and the handler still calls `s.Processor().ApplicationDataInfluenceDataSubsToNotifyGetProcedure(c, dnn,snssai, internalGroupId, supi)` defined in  `./free5gc_4-2-1/free5gc/NFs/udr/internal/sbi/processor/influence_data_subscriptions_collection.go`.
4. This processor function queries the data repository and writes the full list of Traffic Influence Subscriptions to the HTTP response body, including `supis` fields with SUPI/IMSI values.

As a result, a request without any query parameters produces a response where the HTTP status is 400 Bad Request, but the body contains both the error object and the full subscription list.

The missing `return` after sending the 400 response in `api_datarepository.go` is the root cause of this vulnerability.

### PoC
No authentication, no prior knowledge of any subscriber identifier required.

```bash
curl -v "http://<udr-host>/nudr-dr/v2/application-data/influenceData/subs-to-notify"
```
Response (HTTP 400):
```json
{"status":400,"detail":"At least one of DNNs, S-NSSAIs, Internal Group IDs or SUPIs shall be provided"}
[{"dnns":["internet"],
  "snssais":[{"sst":1,"sd":"000001"}],
  "supis":["imsi-222777483957498"],
  "notificationUri":"http://pcf.../npcf-callback/v1/nudr-notify/influence-data/imsi-222777483957498/1"}]
```

### Impact
This is an unauthenticated information disclosure vulnerability. Any attacker with network access to the SBI (Service Based Interface) can enumerate SUPIs (Subscriber Permanent Identifiers / IMSI values) of registered users without any credentials or prior knowledge.

In a 5G network, the SUPI is the most sensitive subscriber identifier — its exposure breaks the privacy guarantees introduced by 3GPP with the SUCI (Subscription Concealed Identifier) mechanism, designed specifically to prevent SUPI tracking over the air. This vulnerability completely undermines that protection at the core network level.

Impacted deployments: any free5GC instance where the SBI is reachable by untrusted parties (e.g., misconfigured network segmentation, rogue NF, or compromised internal host).

Note: an additional trigger exists — sending a malformed `snssai` parameter  also bypasses validation due to a missing return after the deserialization  error handler, producing the same information disclosure.

### Patch

The vulnerability has been confirmed patched by adding the two missing `return` statements in `NFs/udr/internal/sbi/api_datarepository.go`, function `HandleApplicationDataInfluenceDataSubsToNotifyGet`:

1. After the `c.JSON(http.StatusBadRequest, problemDetails)` call in the `snssai` deserialization error branch.
2. After the `c.JSON(http.StatusBadRequest, problemDetails)` call in the empty parameters validation block.

With the patch applied, a request without any query parameters now correctly returns HTTP 400 with only the error message, and no subscriber data is included in the response body.

The fix has been verified: after applying the patch and recompiling the UDR, the endpoint `GET /nudr-dr/v2/application-data/influenceData/subs-to-notify` returns HTTP 400 with only:
```
{"status":400,"detail":"At least one of DNNs, S-NSSAIs, Internal Group IDs 
or SUPIs shall be provided"}
```
No SUPI or subscription data is leaked.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-wrwh-rpq4-87hf
- https://nvd.nist.gov/vuln/detail/CVE-2026-40245
- https://github.com/free5gc/udr
