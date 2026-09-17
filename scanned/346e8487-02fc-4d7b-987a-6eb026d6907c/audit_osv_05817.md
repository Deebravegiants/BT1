# [M] BIT-hyperledger-fabric-orderer-2024-45244

## Summary
Severity: Medium
Advisory: BIT-hyperledger-fabric-orderer-2024-45244
Aliases: BIT-hyperledger-fabric-peer-2024-45244, BIT-hyperledger-fabric-tools-2024-45244, CVE-2024-45244, GHSA-48gg-32q2-4r6m, GO-2024-3099
Ecosystem: Bitnami
Published: 2024-09-13
Source: https://osv.dev/vulnerability/BIT-hyperledger-fabric-orderer-2024-45244
Type: osv

## Affected
- Bitnami: `hyperledger-fabric-orderer` — affected >=0 <2.5.10

## Details
Hyperledger Fabric through 3.0.0 and 2.5.x through 2.5.9 do not verify that a request has a timestamp within the expected time window.

## References
- https://github.com/hyperledger/fabric/commit/155457a6624b3c74b22e5729c35c8499bfe952cd
- https://nvd.nist.gov/vuln/detail/CVE-2024-45244
- https://github.com/shanker-sec/HLF_TxTime_spoofing
- https://github.com/shanker-sec/hlf-time-oracle
