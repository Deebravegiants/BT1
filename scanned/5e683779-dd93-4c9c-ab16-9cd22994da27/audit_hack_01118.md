# [M] zkSync incident: According to official news, the zkSync team announced the cause of the downtime on Twitter. Block generation stopped due to a bloc

## Summary
Severity: Medium
Target: zkSync
Loss: -
Attack method: Downtime
Published: 2023-04-02
Source: https://twitter.com/zksync/status/1642277369632227334
Type: slowmist-incident

## Details
According to official news, the zkSync team announced the cause of the downtime on Twitter. Block generation stopped due to a block queue database failure. Despite this, the server API was not affected. Transactions continue to be added to the mempool, and queries are served normally. Although all components had comprehensive monitoring, logging, and alerting, no alerts were triggered because the API was functioning properly.
