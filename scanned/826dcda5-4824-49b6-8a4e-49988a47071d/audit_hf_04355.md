# [M] The signatures are replayable

## Summary
Severity: Medium
Contest weight: 0.6277
Dataset id: 21519
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract allows a user to sign an order that is later executed by an operator, but the signed order does not contain a nonce or any unique identifier and the execution function does not verify that the on‑chain parameters match the data the user signed. The validation routine only recovers the signer address from the signature and checks that the order has not been explicitly cancelled. Because the order hash is static, the same signature can be submitted repeatedly and the operator can arbitrarily change fields such as deadline, liquidity amount, target token, or swap data without breaking the signature check. An attacker who controls the OPERATOR_ROLE – either through key compromise, a breached backend API, or a software bug that re‑uses stored orders – can replay a previously signed order or craft a new execution that uses the old signature while supplying malicious parameters. This can lead to unexpected position adjustments, removal of liquidity, creation of extra NFTs, or loss of funds from the user’s wallet. From the user’s perspective the symptoms may be a sudden drop of token balances to zero, receipt of an extra NFT that holds no value, or a failed swap where the expected output is missing. The issue was discovered during a formal audit when a test case signed an empty order struct and the contract executed it successfully, proving that the signed data is never compared to the execution payload. The bug is hard to notice because the signature verification passes, giving the impression that the transaction is authorized, while the underlying business logic – that the user’s intent is respected – is violated. The vulnerability belongs to the class of replayable signature or missing‑nonce bugs combined with insufficient parameter binding. To remediate, the order struct should include a nonce (or a unique order identifier) that is stored and marked as used after execution, and the execute function must compare every relevant field of the signed order with the parameters supplied by the operator, rejecting any mismatch. This ensures that each signed order can be used only once and that the operator cannot alter the user‑intended transaction details.

## Proof of Concept
All orders managed by the Krystal team are signed by the user, executed by the operator and the signature is verified on-chain:

```solidity
src/V3Automation.sol
    function execute(ExecuteParams calldata params) public payable onlyRole(OPERATOR_ROLE) whenNotPaused() {
        require(_isWhitelistedNfpm(address(params.nfpm)));
        address positionOwner = params.nfpm.ownerOf(params.tokenId);
        _validateOrder(params.userOrder, params.orderSignature, positionOwner);
        _execute(params, positionOwner);
    }
//[...]
    function _validateOrder(StructHash.Order memory order, bytes memory orderSignature, address actor) internal view {
        address userAddress = recover(order, orderSignature);
        require(userAddress == actor);
        require(!_cancelledOrder[keccak256(orderSignature)]);
    }

src/EIP712.sol
    function recover(StructHash.Order memory order, bytes memory signature) internal view returns (address) {
        bytes32 digest = _hashTypedDataV4(StructHash._hash(order));
        return ECDSA.recover(digest, signature);
    }
```

However, there is no nonce field in the [StructHash.Order](https://github.com/code-423n4/2024-06-krystal-defi/blob/f65b381b258290653fa638019a5a134c4ef90ba8/src/StructHash.sol). That means that the same hashed order can be reused multiple times. 

What’s also important is that the order is used only to verify if it was signed by the user, however it’s not checked if the order that user signed is the same as the params passed by the operator, because [ExecuteParams](https://github.com/code-423n4/2024-06-krystal-defi/blob/f65b381b258290653fa638019a5a134c4ef90ba8/src/V3Automation.sol#L40-L82) sent to `V3Automation.execute()` use other set of params to indicate the action to perform:

```solidity
    struct ExecuteParams {
        Action action;
        Protocol protocol;
        INonfungiblePositionManager nfpm;

        uint256 tokenId;
        uint128 liquidity; // liquidity the calculations are based on

        // target token for swaps (if this is address(0) no swaps are executed)
        address targetToken;

        uint256 amountIn0;
        // if token0 needs to be swapped to targetToken - set values
        uint256 amountOut0Min;
        bytes swapData0;
        //[...]
        // user signed config
        StructHash.Order userOrder;
        bytes orderSignature;
    }
```

And later in the function, `params.userOrder` is not used, only the params prepared by the operator:

```solidity
src/V3Automation.sol
    if (params.action == Action.AUTO_ADJUST) {
        require(state.tickLower != params.newTickLower || state.tickUpper != params.newTickUpper);
        SwapAndMintResult memory result;
        if (params.targetToken == state.token0) {
            result = _swapAndMint(SwapAndMintParams(params.protocol, params.nfpm, IERC20(state.token0), IERC20(state.token1), state.fee, params.newTickLower, params.newTickUpper, 0, state.amount0, state.amount1, 0, positionOwner, params.deadline, IERC20(state.token1), params.amountIn1, params.amountOut1Min, params.swapData1, 0, 0, bytes(""), params.amountAddMin0, params.amountAddMin1), false);
        } else if (params.targetToken == state.token1) {
            result = _swapAndMint(SwapAndMintParams(params.protocol, params.nfpm, IERC20(state.token0), IERC20(state.token1), state.fee, params.newTickLower, params.newTickUpper, 0, state.amount0, state.amount1, 0, positionOwner, params.deadline, IERC20(state.token0), 0, 0, bytes(""), params.amountIn0, params.amountOut0Min, params.swapData0, params.amountAddMin0, params.amountAddMin1), false);
        } else {
            // Rebalance without swap
            result = _swapAndMint(SwapAndMintParams(params.protocol, params.nfpm, IERC20(state.token0), IERC20(state.token1), state.fee, params.newTickLower, params.newTickUpper, 0, state.amount0, state.amount1, 0, positionOwner, params.deadline, IERC20(address(0)), 0, 0, bytes(""), 0, 0, bytes(""), params.amountAddMin0, params.amountAddMin1), false);
        }
```

Actually, this behavior is shown in [test/integration/V3Automation.t.sol](https://github.com/code-423n4/2024-06-krystal-defi/blob/f65b381b258290653fa638019a5a134c4ef90ba8/test/integration/V3Automation.t.sol#L13-L73):

```solidity
    StructHash.Order emptyUserConfig; // todo: remove this when we fill user configuration

    function setUp() external {
        _setupBase();
    }

    function testAutoAdjustRange() external {
        // add liquidity to existing (empty) position (add 1 DAI / 0 USDC)
        _increaseLiquidity();
        (address userAddress, uint256 privateKey) = makeAddrAndKey("positionOwnerAddress");

        vm.startPrank(TEST_NFT_ACCOUNT);
        NPM.safeTransferFrom(TEST_NFT_ACCOUNT, userAddress, TEST_NFT);
        vm.stopPrank();

        bytes memory signature = _signOrder(emptyUserConfig, privateKey);

        uint256 countBefore = NPM.balanceOf(userAddress);

        (, , , , , , , uint128 liquidityBefore, , , , ) = NPM.positions(
            TEST_NFT
        );

        V3Automation.ExecuteParams memory params = V3Automation.ExecuteParams(
            V3Automation.Action.AUTO_ADJUST,
            Common.Protocol.UNI_V3,
            NPM,
            TEST_NFT,
            liquidityBefore,
            address(USDC),
            500000000000000000,
            400000,
            _get05DAIToUSDCSwapData(),
            0,
            0,
            "",
            0,
            0,
            block.timestamp,
            184467440737095520, // 0.01 * 2^64
            0,
            MIN_TICK_500,
            -MIN_TICK_500,
            true,
            0,
            0,
            emptyUserConfig,
            signature
        );

        // using approve / execute pattern
        vm.prank(userAddress);
        NPM.setApprovalForAll(address(v3automation), true);

        vm.prank(TEST_OWNER_ACCOUNT);

        v3automation.execute(params);

        // now we have 2 NFTs (1 empty)
        uint256 countAfter = NPM.balanceOf(userAddress);
        assertGt(countAfter, countBefore);

        (, , , , , , , uint128 liquidityAfter, , , , ) = NPM.positions(
            TEST_NFT
        );
        assertEq(liquidityAfter, 0);
    }
```

In the test above, `emptyUserConfig` - being really empty, i.e. consisting of only 0s, because it’s not being set - is being signed and the order successfully executes, even though the action adds liquidity. That means that the `deadline`, `liquidity` to get, `recipient` of the funds, `amount` , etc. - basically all parameters that the user signs are independent from what is being sent on-chain.

To summarize, there are multiple occasions, where no nonce and actually no verification of execute params conformity to under signed order can be exploited:

* Purposeful action
  * private operator key compromise
* Accidental action
  * Backend API breach
  * software failure leading to sending other orders than users signed
  * sending the same order multiple times due to local database failure

## Recommendation
Introduce nonce and verification that operator parameters are the same that the user signed.

> Confirming as Medium. There is the concrete possibility of fund loss, however, the `onlyRole(OPERATOR_ROLE)` privilege required to exploit it mitigates the risk.

**namnm1991 (Krystal DeFi) acknowledged**
