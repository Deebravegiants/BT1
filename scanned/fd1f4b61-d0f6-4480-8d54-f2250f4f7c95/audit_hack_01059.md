# [M] Move VM incident: Recently, a security firm discovered a stack overflow vulnerability in the Move VM that does not limit the depth of recursive call

## Summary
Severity: Medium
Target: Move VM
Loss: -
Attack method: Overflow Vulnerability
Published: 2023-06-15
Source: https://www.panewslab.com/zh/sqarticledetails/b678w3tm.html
Type: slowmist-incident

## Details
Recently, a security firm discovered a stack overflow vulnerability in the Move VM that does not limit the depth of recursive calls, which can cause a total network shutdown, prevent new validator nodes from joining the network, and potentially even cause a hard fork. mainnet_v1.2.1, Aptos mainnet_v1.4.3 and earlier are all affected by this vulnerability. Suimainnet_v1.2.1, Aptosmainnet_v1.4.3, and Move-language versions after June 10, 2023 fix this vulnerability.
