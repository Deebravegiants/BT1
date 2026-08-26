# [M] fabric-chaincode-java: TLS Private Key Password Disclosed in INFO Startup Logs in Chaincode-as-a-Service Mode

## Summary
Severity: Medium
Chain: org.hyperledger.fabric-chaincode-java:fabric-chaincode-shim
Component: org.hyperledger.fabric-chaincode-java:fabric-chaincode-shim
CVE: CVE-2026-45581
CWE: Insertion of Sensitive Information into Log File
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-wg5x-3g47-v38r
Type: github-advisory

## Details
When chaincode is deployed in chaincode-as-a-service mode with TLS enabled, the chaincode server INFO level logging includes the TLS private key password in plaintext. An attacker with access to the chaincode server logs could recover the TLS private key password. If the attacker can also obtain the TLS private key, they could impersonate the chaincode server.

### Recommendation

- Update to the fixed version of the chaincode runtime.
- Redact or remove existing logs that contain the TLS private key password.
- Change the TLS private key password.

### Mitigation

Impacted deployments can mitigate the vulnerability by restricting the logging level to WARNING or higher so that INFO level logs are not written.
