# [M] Missing Timeout in `RPC.call`

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Within the dependency `iso-filecoin`, there's an oversight in the RPC class. Specifically, the `call` method lacks a timeout parameter. Due to this missing timeout, the snap execution can experience delays, which could lead to an aborted request. The code excerpt provided shows the missing timeout in the fetch call.

```typescript
const res = await this.fetch(this.api, {
  method: 'POST',
  headers: this.headers,
  body: JSON.stringify({
    jsonrpc: '2.0',
    method,
    params,
    id: 1,
  }),
})
```

#### Recommendation

To mitigate potential delays and ensure smoother operation, it's recommended to introduce a timeout to this `call` method. Implementing a timeout can prevent prolonged waits and enhance the resilience of the method against unexpected delays.
