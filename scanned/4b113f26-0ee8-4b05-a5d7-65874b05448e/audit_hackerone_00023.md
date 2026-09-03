# [M] POST /api/bitcoinWithdrawalFees returns financial data without authentication despite being documented as a USER OPERATION (private endpoint)

## Summary
Severity: Medium
Program: CoinMate.io
Weakness: Improper Authentication - Generic
Reporter: glferreira-devsecops
State: resolved
Disclosed: 2026-05-20T09:26:54.084Z
Source: https://hackerone.com/reports/3676308

## Details
## Summary

The `POST /api/bitcoinWithdrawalFees` endpoint returns real-time Bitcoin withdrawal fee data **without requiring any authentication**, despite being explicitly documented as a **"USER OPERATION"** (private endpoint) in the [official CoinMate API documentation](https://github.com/coinmate-io/coinmate-api-examples/blob/main/resources/doc.md#bitcoin-withdrawal-fees-bitcoinwithdrawalfees).

This is the **only** private endpoint that does not enforce authentication. All other `USER OPERATION` endpoints (e.g., `/api/balances`, `/api/openOrders`, `/api/bitcoinDepositAddresses`) correctly reject unauthenticated requests with `{"error": true, "errorMessage": "Invalid request"}`.

## Root Cause

The authentication middleware/filter on the `/api/bitcoinWithdrawalFees` endpoint is misconfigured, allowing the request to bypass HMAC-SHA256 signature verification. This is confirmed by the fact that all three official API client libraries (Java, TypeScript, Python) invoke this endpoint via their `postPrivate()` methods, which attach `clientId`, `nonce`, `publicKey`, and `signature` parameters.

## Evidence from Official Documentation

From [`resources/doc.md` (line 1230-1246)](https://github.com/coinmate-io/coinmate-api-examples/blob/main/resources/doc.md):

```
## Bitcoin withdrawal fees [/bitcoinWithdrawalFees]
**USER OPERATION**

### POST [POST]
+ Request (application/x-www-form-urlencoded)

        clientId=1038&nonce=15270794730&signature=94933BF157B9405A1C2F330902987300B3A73DE620023E1782635AAF16984729
```

The documentation explicitly shows authentication parameters (`clientId`, `nonce`, `signature`) as **required** for this endpoint.

## Evidence from Official Client Libraries

**TypeScript** ([CoinmateClient.ts](https://github.com/coinmate-io/coinmate-api-examples/blob/main/typescript/src/client/CoinmateClient.ts)):
```typescript
async getBitcoinWithdrawalFees(): Promise<CoinmateResponse<any>> {
    return this.httpClient.postPrivate('/bitcoinWithdrawalFees');
    //                      ^^^^^^^^^^^ — treated as PRIVATE
}
```

**Java** ([CoinmateClient.java](https://github.com/coinmate-io/coinmate-api-examples/blob/main/java/main/java/org/example/coinmate/client/CoinmateClient.java)):
```java
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3676308_
