# [H] Risk of insufficient liquidity

## Summary
Severity: High
Source: https://github.com/neptune-mutual-blue/protocol/blob/73fc82fbe0d1388867b7df669983fe42760daeb1/contracts/libraries/PolicyHelperV1.sol#L50
Type: audit-issue

## Details
When purchasing a cover, the protocol [ensures it has enough funds](https://github.com/neptune-mutual-blue/protocol/blob/73fc82fbe0d1388867b7df669983fe42760daeb1/contracts/libraries/PolicyHelperV1.sol#L50) to pay out all potential claimants. The computation of the [existing commitments](https://github.com/neptune-mutual-blue/protocol/blob/73fc82fbe0d1388867b7df669983fe42760daeb1/contracts/libraries/CoverUtilV1.sol#L477-L481) includes all covers expiring in the next 3 months, since this is the [maximum policy duration](https://github.com/neptune-mutual-blue/protocol/blob/133bc8a4157d4f27471b0cf43ac0ce2b51bb5e5a/contracts/libraries/ProtoUtilV1.sol#L14). However, some covers may expire [in the fourth month](https://github.com/neptune-mutual-blue/protocol/blob/73fc82fbe0d1388867b7df669983fe42760daeb1/contracts/libraries/CoverUtilV1.sol#L609) and these would be excluded from the calculation. Therefore, the protocol could sell more insurance than it can support, and some valid claimants may be unable to retrieve their payment.

Consider including the extra month in the commitment computation.

**Update:** _Fixed as of commit `63fce22c67f72cf090ffa124784a3d92935e2d66` in [pull request #136](https://github.com/neptune-mutual-blue/protocol/pull/136)._
