# [C] Remote code execution in Indy-Node's pool-upgrade transaction

## Summary
Severity: Critical
Chain: Hyperledger Indy
Component: hyperledger/indy-node
CVE: CVE-2022-31020
Published: 2022-09-02
Source: https://github.com/hyperledger-indy/indy-node/security/advisories/GHSA-r6v9-p59m-gj2p
Type: github-advisory

## Details
### Impact

The `pool-upgrade` request handler in Indy-Node `<=1.12.4` allows an improperly authenticated attacker to remotely execute code on nodes within the network.

Network operators are strongly encouraged to upgrade to the latest Indy-Node release `>=1.12.5` as soon as possible.

### Patches

The `pool-upgrade` request handler in Indy-Node `>=1.12.5` has been updated to properly authenticate `pool-upgrade` transactions before any processing is performed by the request handler.  The transactions are further sanitized to prevent remote code execution.

### Mitigations

Network operators are strongly encouraged to upgrade to the latest Indy-Node release `>=1.12.5` as soon as possible.

### Acknowledgements
Thank you to @shakreiner at CyberArk Labs for finding and responsibly disclosing this issue.
