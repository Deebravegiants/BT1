# [C] Uncontrolled Resource Consumption in Indy Node

## Summary
Severity: Critical
Advisory: GHSA-3gw4-m5w7-v89c
CVE: CVE-2020-11090
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-06-11
Source: https://github.com/advisories/GHSA-3gw4-m5w7-v89c
Type: github-advisory

## Affected
- PyPI: `indy-node` — affected >=1.12.2 <1.12.3

## Details
# Summary
Indy Node has a bug in TAA handling code. The current primary can be crashed with a malformed transaction from a client, which leads to a view change. Repeated rapid view changes have the potential of bringing down the network.

# Discovery
On May 18, Evernym's monitoring of Sovrin StagingNet showed a report of StagingNet losing sufficient consensus to validate write transactions. The problem resolved itself within a few minutes. On May 20th we saw the alert multiple times, and we began analyzing the logs of our steward node. On May 21st we continued to see the alerts with increasing frequency.

It appears that someone is unknowingly sending a malformed transaction, and retrying when the transaction fails. The cause of the errors appear to be the TAA acceptance.

# Proposed actions
* Reproduce problem in integration tests and create a fix
* Do a hotfix release branching from last stable (current master have some things merged that are too risky)
* Upgrade BuilderNet, StagingNet and MainNet as soon as possible
* Improve testing strategy on Indy Node to reduce probability of such bugs

# Notes
* The journalctl logs also show an out-of-memory problem on the Australia node. We need to evaluate if this should be raised as a separate issue.

## References
- https://github.com/hyperledger/indy-node/security/advisories/GHSA-3gw4-m5w7-v89c
- https://nvd.nist.gov/vuln/detail/CVE-2020-11090
- https://github.com/hyperledger/indy-node
- https://github.com/hyperledger/indy-node/blob/master/CHANGELOG.md#1123
- https://github.com/pypa/advisory-database/tree/main/vulns/indy-node/PYSEC-2020-47.yaml
- https://pypi.org/project/indy-node/1.12.3
