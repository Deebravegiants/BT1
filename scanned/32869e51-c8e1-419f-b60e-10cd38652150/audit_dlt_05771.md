# [M] Attacker can grief a user by making his supplyW...

## Summary
Severity: Medium
Chain: Smart contract
Component: ZeroLend
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28970%20-%20%5BSC%20-%20Medium%5D%20Attacker%20can%20grief%20a%20user%20by%20making%20his%20supplyW....md
Type: immunefi-boost

## Details
Target: https://pacific-explorer.manta.network/address/0x8676e39B5D2f0d6E0d78a4208a0cCBc50504972e

## Description

## Brief/Intro

When a user calls `supplyWithPermit` function, attacker can make the call revert by front-running. This happens because of a missing `try-catch` statement in the `supplyWithPermit` function.

## Vulnerability Details

When `supplyWithPermit` is called, by passing a permit signature, the contract calls the `permit` function of the asset to get approval to spend on behalf of caller. It then calls the `SupplyLogic.executeSupply` function to supply the asset.

So an attacker sees the `supplyWithPermit` call in the mempool, and extracts the permit signature from the call's argument. Attacker then use this permit signature, to directly call the asset's `permit` function. This will give the approval to the contract address, but along with it will increase the user's nonce, thus making the signature invalid for any further use.

Due to this when the original `supplyWithPermit` gets mined, it will revert, as the signature has become invalid. Hence the user's transaction will revert.

## Impact Details

Attacker can grief users by frontrunning the `supplyWithPermit` functions, making that functionality unusable by users. Apart from `supplyWithPermit` the `repayWithPermit` function is also vulnerable to this issue.

## Remediation Details

Implement a try-catch statement. Inside the `supplyWithPermit` function, call the assets `permit` statement using a try statement, and catch any revert. That will resolve the issue.

## References

https://www.trust-security.xyz/post/permission-denied

## Proof of Concept

Here is the test file. The specific test case showing the vulnerability is "Supply with permit test'"

```
import { expect } from 'chai';
import { BigNumber, Signer, utils } from 'ethers';
import { impersonateAccountsHardhat } from '../helpers/misc-utils';
import { ProtocolErrors, RateMode } from '../helpers/types';
import { getFirstSigner } from '@aave/deploy-v3/dist/helpers/utilities/signer';
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28970%20-%20%5BSC%20-%20Medium%5D%20Attacker%20can%20grief%20a%20user%20by%20making%20his%20supplyW....md_
