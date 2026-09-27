# [H] BIT-hyperledger-fabric-orderer-2022-45196

## Summary
Severity: High
Advisory: BIT-hyperledger-fabric-orderer-2022-45196
Aliases: BIT-hyperledger-fabric-peer-2022-45196, BIT-hyperledger-fabric-tools-2022-45196, CVE-2022-45196
Ecosystem: Bitnami
Published: 2024-07-18
Source: https://osv.dev/vulnerability/BIT-hyperledger-fabric-orderer-2022-45196
Type: osv

## Affected
- Bitnami: `hyperledger-fabric-orderer` — affected >=2.3.0 <2.3.1

## Details
Hyperledger Fabric 2.3 allows attackers to cause a denial of service (orderer crash) by repeatedly sending a crafted channel tx with the same Channel name. NOTE: the official Fabric with Raft prevents exploitation via a locking mechanism and a check for names that already exist.

## References
- https://github.com/SmartBFT-Go/fabric/issues/286
- https://github.com/hyperledger/fabric/pull/2934
- https://nvd.nist.gov/vuln/detail/CVE-2022-45196
