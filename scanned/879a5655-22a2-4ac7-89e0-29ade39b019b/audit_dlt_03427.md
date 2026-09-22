# [H] `executeWithdraw` may be blocked if any of the users are blacklisted from the `baseToken`

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1426
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L428


# Vulnerability details

https://github.com/d-xo/weird-erc20#tokens-with-blocklists

> Some tokens (e.g. `USDC`, `USDT`) have a contract level admin controlled address blocklist. If an address is blocked, then transfers to and from that address are forbidden.

> Malicious or compromised token owners can trap funds in a contract by adding the contract address to the blocklist. This could potentially be the result of regulatory action against the contract itself, against a single user of the contract (e.g. a Uniswap LP), or could also be a part of an extortion attempt against users of the blocked contract.

If a user whose address has been blocklisted is added to a `withdrawQueue` inside the `AccountingManager` contract, all other users that are in that same queue will not be able to withdraw, as the `executeWithdraw` function will revert when it tries to do `[baseToken.safeTransfer](https://github.com/code-423n4/2024-04-noya/blob/main/contracts/accountingManager/AccountingManager.sol#L428)` call on the blocklisted address.

## Impact

A user who has been blocklisted can be added to a `withdrawQueue` to DoS the call of the `executeWithdraw` function, effectively preventing all other user that are in that same queue from withdrawing, locking their assets inside the protocol.

## Proof of Concept

When `baseToken` has blocklisting functionality, and any user in the withdrawal queue is in the blocklist, it prevents all other users from making withdrawals.

_Place the following test in [testFoundry/BlacklistableTokenPOC.t.sol](https://github.com/code-423n4/2024-04-noya/tree/9c79b332eff82011dcfa1e8fd51bad805159d758/testFoundry) and run it with the command `forge test --mt testBlacklistableERC20`_

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.20;

import "@openzeppelin/contracts-5.0/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts-5.0/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts-5.0/token/ERC20/ERC20.sol";
import "./utils/testStarter.sol";
import "./utils/resources/OptimismAddresses.sol";
import { AaveConnector, BaseConnectorCP } from "contracts/connectors/AaveConnector.sol";

contract BlacklistERC20 is ERC20 {
    mapping(address => bool) private blacklisted;

    error AccountBlacklisted();

    constructor() ERC20("Blacklist ERC20", "BLT") {
        _mint(msg.sender, 100e18);
    }

    function addToBlacklist(address account) public  {
        blacklisted[account] = true;
    }

    function isBlacklisted(address account) public view returns (bool) {
        return blacklisted[account];
    }

    function _update(
        address from,
        address to,
        uint256 value
    ) internal override {
        if (isBlacklisted(from) || isBlacklisted(to)) revert AccountBlacklisted();
        super._update(from, to, value);
    }
}

contract BlacklistableTokenPOC is testStarter, OptimismAddresses  {
   using SafeERC20 for IERC20;

    AaveConnector connector;

    address charlie = makeAddr("charlie");

    address public constant USD = address(840);

    BlacklistERC20 token;

    function setUp() public {
        vm.label(alice, "alice");
        vm.label(bob, "bob");
        vm.label(charlie, "charlie");

        vm.startPrank(owner);
        token = new BlacklistERC20();

        deployEverythingNormal(address(token));

        connector = new AaveConnector(aavePool, USD, BaseConnectorCP(registry, 0, swapHandler, noyaOracle));
        addConnectorToRegistry(vaultId, address(connector));
        addTrustedTokens(vaultId, address(accountingManager), address(token));

        registry.addTrustedPosition(vaultId, connector.AAVE_POSITION_ID(), address(connector), true, false, "", "");
        registry.addTrustedPosition(vaultId, 0, address(accountingManager), false, false, abi.encode(address(token)), "");

        vm.stopPrank();
    }

    function testBlacklistableERC20() public {
        uint depositAmount = 10e18;

        // give tokens to the users
        vm.startPrank(owner);
        token.transfer(alice, depositAmount);
        token.transfer(bob, depositAmount);
        token.transfer(charlie, depositAmount);
        vm.stopPrank();

        // user's deposits
        vm.startPrank(alice);
        SafeERC20.forceApprove(IERC20(token), address(accountingManager), depositAmount);
        accountingManager.deposit(address(alice), depositAmount, address(0));
        vm.stopPrank();

        vm.startPrank(bob);
        SafeERC20.forceApprove(IERC20(token), address(accountingManager), depositAmount);
        accountingManager.deposit(address(bob), depositAmount, address(0));
        vm.stopPrank();

        vm.startPrank(charlie);
        SafeERC20.forceApprove(IERC20(token), address(accountingManager), depositAmount);
        accountingManager.deposit(address(charlie), depositAmount, address(0));
        vm.stopPrank();

        // manager execute deposits
        vm.startPrank(owner);
        accountingManager.calculateDepositShares(10);
        skip(accountingManager.depositWaitingTime());
        accountingManager.executeDeposit(10, address(connector), "");
        vm.stopPrank();

        // withdraw requests
        vm.startPrank(alice);
        accountingManager.withdraw(accountingManager.maxRedeem(alice), address(alice));
        vm.stopPrank();

        vm.startPrank(bob);
        accountingManager.withdraw(accountingManager.maxRedeem(bob), address(bob));
        vm.stopPrank();

        vm.startPrank(charlie);
        accountingManager.withdraw(accountingManager.maxRedeem(charlie), address(charlie));
        vm.stopPrank();

        // execute withdraw
        vm.startPrank(owner);
        accountingManager.calculateWithdrawShares(10);
        accountingManager.startCurrentWithdrawGroup();
        uint neededAssetsForWithdraw = accountingManager.neededAssetsForWithdraw();
        RetrieveData[] memory retrieveData = new RetrieveData[](1);
        retrieveData[0] = RetrieveData(
            neededAssetsForWithdraw,
            address(connector),
            abi.encode(neededAssetsForWithdraw, ""));
        accountingManager.retrieveTokensForWithdraw(retrieveData);
        skip(accountingManager.withdrawWaitingTime());
        accountingManager.fulfillCurrentWithdrawGroup();

        // @audit When one of the users is blacklisted from the baseToken, no one else can withdraw either
        token.addToBlacklist(alice);

        vm.expectRevert();
        accountingManager.executeWithdraw(10);
    }
}
```

## Tools Used

Manual Review

## Recommended Mitigation Steps

Validate that the receiver is not blacklisted before making the `ERC20::safeTransfer` call, whenever the `baseToken` has a contract level admin controlled address blocklist (e.g. `USDC`, `USDT`).

```diff
function executeWithdraw(uint256 maxIterations) public onlyManager nonReentrant whenNotPaused {
			...
        while (
            currentWithdrawGroup.lastId > firstTemp
                && withdrawQueue.queue[firstTemp].calculationTime + withdrawWaitingTime <= block.timestamp // @audit-info use withdrawRequest time
                && i < maxIterations
        ) {
            i += 1;
            WithdrawRequest memory data = withdrawQueue.queue[firstTemp];
            uint256 shares = data.shares;
            // calculate the base token amount that the user will receive based on the total available amount
            uint256 baseTokenAmount =
                data.amount * currentWithdrawGroup.totalABAmount / currentWithdrawGroup.totalCBAmountFullfilled;

            withdrawRequestsByAddress[data.owner] -= shares;

            _burn(data.owner, shares);

            processedBaseTokenAmount += data.amount;
            {
                uint256 feeAmount = baseTokenAmount * withdrawFee / FEE_PRECISION;
                withdrawFeeAmount += feeAmount;
                baseTokenAmount = baseTokenAmount - feeAmount;
            }

+           if (baseToken.isBlacklisted(data.receiver)) {
+	        continue;
+	    }

            baseToken.safeTransfer(data.receiver, baseTokenAmount);

            emit ExecuteWithdraw(
                firstTemp, data.owner, data.receiver, shares, data.amount, baseTokenAmount, block.timestamp
            );

            delete withdrawQueue.queue[firstTemp];
            firstTemp += 1;
        }
			...
    }
```



## Assessed type

ERC20
