No Vulnerability found for this question.

The SFPM bug is specific to Panoptic's ERC-1155 position-NFT model, where a single `tokenId` encodes multiple "legs," each keyed by a `positionKey`, and the post-transfer hook requires `netLiquidity == chunk.liquidity()` per leg — a condition that breaks when the same position key is touched by multiple legs/tokenIds. alt.fun has no analogous data structure anywhere in its allowed attack surface.

- `Token` is a plain `ERC20` (burnable/ownable), not an `ERC1155`, and carries no leg/position-key concept at all.
- `Pair` tracks only two scalar reserves (`reserve0`/`reserve1`) and a single `k`, with no per-account liquidity-chunk bookkeeping that could be "touched multiple times." [1](#0-0) 
- `Bonding`, `Zap`, and `FeeVault` operate on flat balances (curve reserves, USDC fee pools, creator/protocol counters) rather than any netted "liquidity per key" abstraction that could be double-counted across legs. [2](#0-1) 
- `LPLock.recordLock` is a one-shot record of a single LP amount, not a multi-leg position ledger, so there is no "duplicate position key across legs" scenario to violate. [3](#0-2) 

None of the permitted unprivileged entry points (`Zap.createToken/buy/sell`, `Bonding.triggerGraduation/finalizeGraduation/transferCreator`, `FeeVault.claim/claimProtocol/sweepDonations`, direct ERC20 transfers of Token/LT into Pair/Bonding/Zap/FeeVault, or pre-seeding the HyperSwap pair) reach any code path resembling SFPM's leg-liquidity equality check, so the bug class does not transplant onto alt.fun's real shape.

### Citations

**File:** packages/contracts/src/Router.sol (L172-182)
```text
    function _computeSell(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 assetOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        uint256 newReserveToken = reserveToken + amountIn;
        assetOut = reserveAsset - (k / newReserveToken);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1027-1033)
```text
        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
```

**File:** packages/contracts/src/Bonding.sol (L1042-1052)
```text
    function _sweepLTToOwner(
        address lt,
        uint256 keep
    ) internal {
        uint256 bal = IERC20(lt).balanceOf(address(this));
        if (bal <= keep) return;
        uint256 amount = bal - keep;
        address recipient = owner();
        IERC20(lt).safeTransfer(recipient, amount);
        emit LTRescued(lt, recipient, amount);
    }
```
