# [H] DOS vulnerability for Hyperledger Indy

## Summary
Severity: High
Chain: Hyperledger Indy
Component: hyperledger/indy-node
CVE: CVE-2022-31006
Published: 2022-09-09
Source: https://github.com/hyperledger-indy/indy-node/security/advisories/GHSA-x996-7qh9-7ff7
Type: github-advisory

## Details
### Impact

An attacker can max out the number of client connections allowed by the ledger that was deployed using guidance provided in the indy-node repository, leaving the ledger unable to be used for its intended purpose.

The ledger content will not be impacted by the attack, and the ledger will resume servicing valid client requests after the attack.

### Mitigations

This attack exploits the trade-off between resilience and availability. Any protection against abusive client connections will also prevent the network being accessed by certain legitimate users. As a result, validator nodes must tune their firewall rules to ensure the right trade-off for their network's expected users. The guidance previously provided enabled a low-cost DDoS attack.

The [guidance to network operators for the use of firewall rules](https://github.com/hyperledger/indy-node/blob/main/docs/source/setup-iptables.md) in the deployment of Indy networks has been modified to better protect against denial of service attacks by increasing the cost and complexity in mounting such attacks.

The mitigation for this vulnerability is not in the Hyperledger Indy code per se, but rather in the individual deployments of Indy. The mitigations should be applied to all deployments of Indy, and are not related to a particular release.

### Acknowledgements

Thank you to Mirko Mollik at [TrustCerts.de](https://trustcerts.de) for finding and responsibly disclosing this issue.
