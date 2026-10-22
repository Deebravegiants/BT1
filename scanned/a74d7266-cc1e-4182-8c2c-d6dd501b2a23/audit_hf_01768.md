# [M] PerpetualVault can be completely bricked

## Summary
Severity: Medium
Contest weight: 0.5950
Dataset id: 9791
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the GMX integration notes, there is a possibility that two handlers may temporarily exist at the same time. As a result, the callback contract must be able to accept calls from multiple handlers. However, the gmxProxy contract does not implement this functionality to whitelist multiple handlers, leading to a critical issue. This limitation can severely impact the vault, potentially rendering it completely inoperable.

According to the GMX integration notes, points 8 and 9 state:

When creating a callback contract, the callback contract may need to whitelist the DepositHandler, OrderHandler, or WithdrawalHandler. It should be noted that new versions of these handlers may be deployed as new code is added to the handlers. Additionally, it is possible for two handlers to temporarily exist at the same time, e.g., OrderHandler(1) and OrderHandler(2). Due to this, the callback contract should be able to whitelist and simultaneously accept callbacks from multiple DepositHandlers, OrderHandlers, and WithdrawalHandlers.

From this, it is evident that multiple OrderHandlers may coexist temporarily. However, the gmxProxy contract currently supports only a single handler at a time, as shown in the validCallback modifier:

```solidity
modifier validCallback(bytes32 key, Order.Props memory order) {
    require(
        msg.sender == address(orderHandler) ||
            msg.sender == address(liquidationHandler) ||
            msg.sender == address(adlHandler),
        "invalid caller"
    );
    require(order.addresses.account == address(this), "not mine");
    _;
}
```

While the updateGmxAddresses() function allows updating handler addresses, it does not account for scenarios where multiple handlers exist simultaneously. This limitation could lead to critical issues.

Consider the following scenario:
The PerpetualVault opens a long/short position on GMX V2.
Bob deposits 100 collateral tokens into the vault, triggering the creation of a MarketIncrease order to increase the position.
The keeper calls runNextAction, which successfully creates the order on GMX V2.
The GMX V2 keeper subsequently executes the order.
At this point, assume that two OrderHandlers exist: OrderHandler(1) and OrderHandler(2), but the gmxProxy contract only accepts callbacks from OrderHandler(1).
If OrderHandler(2) attempts to call afterOrderExecution, the transaction will revert, preventing the necessary state updates in the vault.

Since GMX V2 executes orders using a try/catch block, the order will be executed on GMX V2, and Bob’s funds will be transferred to the GMX V2 vault’s position. However, because the callback was never executed, the vault's state remains inconsistent:
The FLOW state remains in DEPOSIT, preventing further deposits.
Bob does not receive any shares.
If the keeper attempts to call cancelFlow, it will revert due to _gmxLock == true:

```solidity
modifier gmxLock() {
    if (_gmxLock == true) {
        revert Error.GmxLock();
    }
    _;
}
```

Because FLOW remains stuck in DEPOSIT, no further deposits will be possible:

```solidity
function deposit(uint256 amount) external payable nonReentrant {
    _noneFlow();
    ...
}

function _noneFlow() internal view {
    if (flow != FLOW.NONE) {
        revert Error.FlowInProgress();
    }
}
```

Additionally, attempts to cancel the flow will fail:

```solidity
function cancelFlow() external nonReentrant gmxLock {
    _onlyKeeper();
    _cancelFlow();
}
```

POC :

To run the test in PerpetualVault.t.sol, use:

```solidity
forge test --mt testHandlersError --fork-url   --via-ir -vvvv
```

```solidity
function testHandlersError() external {
    IERC20 collateralToken = PerpetualVault(vault).collateralToken();
    address bob = makeAddr("bob");
    uint256 amount = 1e10;
    vm.startPrank(bob);
    deal(address(collateralToken), bob, amount);
    uint256 executionFee = PerpetualVault(vault).getExecutionGasLimit(true);
    collateralToken.approve(vault, amount*3);
    PerpetualVault(vault).deposit{value: executionFee * tx.gasprice}(amount);
    vm.stopPrank();

    MarketPrices memory prices = mockData.getMarketPrices();
    bytes[] memory data = new bytes[](
    data[0] = abi.encode(3380000000000000);
    address keeper = PerpetualVault(vault).keeper();
    vm.startPrank(keeper);
    PerpetualVault(vault).run(true, false, prices, data);
    vm.stopPrank();

    address gmxProxy = address(PerpetualVault(vault).gmxProxy());
    address gmxOwner = GmxProxy(payable(gmxProxy)).owner();

    // taken from setup
    address ethUsdcMarket = address(0x70d95587d40A2caf56bd97485aB3Eec10Bee6336);
    address orderHandler = address(0xe68CAAACdf6439628DFD2fe624847602991A31eB);
    // old address orderHandler = address(0xB0Fc2a48b873da40e7bc25658e5E6137616AC2Ee);
    address liquidationHandler = address(0xdAb9bA9e3a301CCb353f18B4C8542BA2149E4010);
    // old address liquidationHandler = address(0x08A902113F7F41a8658eBB1175f9c847bf4fB9D8);
    address adlHandler = address(0x9242FbED25700e82aE26ae319BCf68E9C508451c);
    // old address adlHandler = address(0x26BC03c944A4800299B4bdfB5EdCE314dD497511);
    address gExchangeRouter = address(0x900173A66dbD345006C51fA35fA3aB760FcD843b);
    // old address gExchangeRouter = address(0x69C527fC77291722b52649E45c838e41be8Bf5d5);
    address gmxRouter = address(0x7452c558d45f8afC8c83dAe62C3f8A5BE19c71f6);
    address dataStore = address(0xFD70de6b91282D8017aA4E741e9Ae325CAb992d8);
    address orderVault = address(0x31eF83a530Fde1B38EE9A18093A333D8Bbbc40D5);
    address gmxReader = address(0x0537C767cDAC0726c76Bb89e92904fe28fd02fE1);
    // address gmxReader = address(0x5Ca84c34a381434786738735265b9f3FD814b824);
    address referralStorage= address(0xe6fab3F0c7199b0d34d7FbE83394fc0e0D06e99d);
    address orderHandler2 = makeAddr("orderHandler2");

    vm.startPrank(gmxOwner);
    GmxProxy(payable(gmxProxy)).updateGmxAddresses(
      orderHandler2,
      liquidationHandler,
      adlHandler,
      gExchangeRouter,
      gmxRouter,
      dataStore,
      orderVault,
      gmxReader,
      referralStorage
    );
    vm.stopPrank();

    (bytes32 requestKey, ) = GmxProxy(payable(gmxProxy)).queue();
    MockData.OracleSetPriceParams memory params = mockData.getOracleParams();
    address gmxKeeper = address(0x6A2B3A13be0c723674BCfd722d4e133b3f356e05);
    vm.prank(gmxKeeper);
    IOrderHandler(orderHandler).executeOrder(requestKey, params);
    
    vm.startPrank(keeper);
    PerpetualVault(vault).cancelFlow();
    vm.stopPrank();
}
```

Logs :

```solidity
Suite result: FAILED. 0 passed; 1 failed; 0 skipped; finished in 49.97ms (37.03ms CPU time)

Ran 1 test suite in 4.02s (49.97ms CPU time): 0 tests passed, 1 failed, 0 skipped (1 total tests)

Failing tests:
Encountered 1 failing test in test/PerpetualVault.t.sol:PerpetualVaultTest
[FAIL: GmxLock()] testHandlersError() (gas: 4905177)

Encountered a total of 1 failing tests, 0 tests succeeded
```

Vault will be completely bricked
Loss of user funds
DOS for the users

## Recommendation
According to GMX integration note

a possible solution would be to validate the role of the msg.sender in the RoleStore, e.g. RoleStore.hasRole(msg.sender, Role.CONTROLLER), this would check that the msg.sender is a valid handler
