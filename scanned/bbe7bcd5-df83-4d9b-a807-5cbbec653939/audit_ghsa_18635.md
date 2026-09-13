# [M] Actual Sync-server Gocardless service is logging sensitive data including bearer tokens and account numbers

## Summary
Severity: Medium
Advisory: GHSA-xvp7-8vm8-xfxx
CWE: CWE-209, CWE-215, CWE-219
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-20
Source: https://github.com/advisories/GHSA-xvp7-8vm8-xfxx
Type: github-advisory

## Affected
- npm: `@actual-app/sync-server` — affected >=0 <25.11.0

## Details
### Summary
The GoCardless components in Actualbudget in are logging responses to STDOUT in a parsed format using `console.log`and `console.debug` (Which in this version of node is an alias for `console.log`). This is exposing sensitive information in log files including, but not limited to:

- Gocardless bearer tokens.
- Account IBAN and Bank Account numbers.
- PII of the account holder.
- Transaction details (Payee bank information, Recipient account numbers, Transaction IDs)...

### Details

Whenever GoCardless responds to a request, the payload is printed to the debug log: 
https://github.com/actualbudget/actual/blob/36c40d90d2fe09eb1f25a6e2f77f6dd40638b267/packages/sync-server/src/app-gocardless/banks/integration-bank.js#L25-L27

This in turn logs the following information to Docker (all values removed here. These fields are possibly dependent on what is returned by each institution so may differ):

```json
{
  "account": {
    "resourceId": "",
    "iban": "",
    "bban": "",
    "currency": "",
    "name": "<full legal name in the bank>",
    "product": "",
    "status": "",
    "bic": "",
    "usage": "",
    "id": "",
    "created": "",
    "last_accessed": "",
    "institution_id": "",
    "owner_name": "",
    "institution": {
      "id": "",
      "name": "",
      "bic": "",
      "transaction_total_days": "",
      "countries": [
        ""
      ],
      "logo": "",
      "max_access_valid_for_days": "",
      "supported_features": [
        "",
        "",
        ""
      ],
      "identification_codes": []
    }
  }
}
```

https://github.com/actualbudget/actual/blob/36c40d90d2fe09eb1f25a6e2f77f6dd40638b267/packages/sync-server/src/app-gocardless/banks/integration-bank.js#L83-L85

This is the first of the 10 transactions:
```json
{
  "top10Transactions": [{
    "transactionId": "",
    "entryReference": "",
    "bookingDate": "",
    "valueDate": "",
    "transactionAmount": {
      "amount": "",
      "currency": ""
    },
    "creditorName": "",
    "creditorAccount": {
      "bban": ""
    },
    "debtorName": "",
    "debtorAccount": {
      "bban": ""
    },
    "remittanceInformationUnstructured": "",
    "remittanceInformationStructuredArray": [
      {"reference": "", "referenceType": ""}
    ],
    "additionalInformation": "",
    "proprietaryBankTransactionCode": "",
    "debtorAgent": "",
    "internalTransactionId": "",
    "payeeName": "",
    "date": ""
  }]
}
```

Additionally, in the error handling for GoCardless, there is a catch all for unclassified errors that prints the entire stack trace to the console.

https://github.com/actualbudget/actual/blob/36c40d90d2fe09eb1f25a6e2f77f6dd40638b267/packages/sync-server/src/app-gocardless/app-gocardless.js#L263-L264

Our bank was offline today for maintenance which threw a 503 error from Gocardless. The entire response payload was dumped to console, which includes the Bearer tokens for accessing GoCardless:

```java
Something went wrong ServiceError: Institution service unavailable
    at handleGoCardlessError (file:///app/src/app-gocardless/services/gocardless-service.js:59:13)
    at Object.getTransactions (file:///app/src/app-gocardless/services/gocardless-service.js:530:7)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async Object.getNormalizedTransactions (file:///app/src/app-gocardless/services/gocardless-service.js:267:26)
    at async file:///app/src/app-gocardless/app-gocardless.js:186:13 {
  details: h [AxiosError]: Request failed with status code 503
      at te (file:///app/node_modules/nordigen-node/dist/index.esm.js:13:914)
      at IncomingMessage.<anonymous> (file:///app/node_modules/nordigen-node/dist/index.esm.js:17:16315)
      at IncomingMessage.emit (node:events:529:35)
      at endReadableNT (node:internal/streams/readable:1400:12)
      at process.processTicksAndRejections (node:internal/process/task_queues:82:21) {
    code: 'ERR_BAD_RESPONSE',
    config: {
      transitional: {
        silentJSONParsing: true,
        forcedJSONParsing: true,
        clarifyTimeoutError: false
      },
      adapter: [ 'xhr', 'http' ],
      transformRequest: [ [Function (anonymous)] ],
      transformResponse: [ [Function (anonymous)] ],
      timeout: 0,
      xsrfCookieName: 'XSRF-TOKEN',
      xsrfHeaderName: 'X-XSRF-TOKEN',
      maxContentLength: -1,
      maxBodyLength: -1,
      env: {
        FormData: [Function: _] {
          LINE_BREAK: '\r\n',
          DEFAULT_CONTENT_TYPE: 'application/octet-stream'
        },
        Blob: [class Blob]
      },
      validateStatus: [Function: validateStatus],
      headers: T [AxiosHeaders] {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Nordigen-Node-v2',
        'Authorization': 'Bearer eyJ0eXAi... (the full token is in the response)',
        'Accept-Encoding': 'gzip, compress, deflate, br'
      },
      method: 'get',
      url: URL {
        href: 'https://bankaccountdata.gocardless.com/api/v2/accounts/<Account id Was Here>?date_from=2024-12-22',
        origin: 'https://bankaccountdata.gocardless.com',
        protocol: 'https:',
        username: '',
        password: '',
        host: 'bankaccountdata.gocardless.com',
        hostname: 'bankaccountdata.gocardless.com',
        port: '',
        pathname: '/api/v2/accounts/<Account id Was Here>/transactions',
        search: '?date_from=2024-12-22',
        searchParams: URLSearchParams { 'date_from' => '2024-12-22' },
        hash: ''
      },
      data: undefined
    },
```
And quite a few pages more.

### PoC
- Setup an Actualbudget server inside of Docker. In this instance I was using the Docker Compose script posted in the repository: https://github.com/actualbudget/actual/blob/master/packages/sync-server/docker-compose.yml
- Link a gocardless account to Actualbudget and sync a bank account
- Observe in the container using `docker logs actual-actual_server-1 -f`  that sensitive details are logged to the console and ingested by docker. 

### Impact
Information disclosure. The services are available both on-premises and in environments that are not under the control of the end user, such as third-party providers who offer this application as a managed solution.

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-xvp7-8vm8-xfxx
- https://github.com/actualbudget/actual/commit/97482a082d502887ef22514b93e35e4c67f4f30f
- https://github.com/actualbudget/actual
- https://github.com/actualbudget/actual/blob/36c40d90d2fe09eb1f25a6e2f77f6dd40638b267/packages/sync-server/src/app-gocardless/app-gocardless.js#L263-L264
- https://github.com/actualbudget/actual/blob/36c40d90d2fe09eb1f25a6e2f77f6dd40638b267/packages/sync-server/src/app-gocardless/banks/integration-bank.js#L25-L27
- https://github.com/actualbudget/actual/blob/36c40d90d2fe09eb1f25a6e2f77f6dd40638b267/packages/sync-server/src/app-gocardless/banks/integration-bank.js#L83-L85
