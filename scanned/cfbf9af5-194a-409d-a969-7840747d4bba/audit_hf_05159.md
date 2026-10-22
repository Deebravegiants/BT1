# [H] Donation fees are sandwich-

## Summary
Severity: High
Contest weight: 0.6372
Dataset id: 23222
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Doesn't matter if MEV is openly possible in the chain, whenever a user does actions like liquidateProtectedListing, cancelListing, modifyListings, fillListings, Reserve and Relist. They can sandwich the fees donation to make profit or recover the tax they paid. Or, the liquidation is open access, so you can sandwich that in same tx itself.
Root cause: allowing more than max donation limit per transaction.
Even if you don't allow to donate more than max, the user will just loop the donation and still extract the $, so it's better to have a max donation per block state that tracks this. So Uniswap openly advises to design the donation mechanism to not allow MEV extraction https://github.com/Uniswap/v4-core/blob/18b223cab19dc778d9d287a82d29fee3e99162b0/src/interfaces/IPoolManager.sol#L167-L172
IPoolManager.sol
```solidity
/// @notice Donate the given currency amounts to the in-range liquidity providers of a pool
/// @dev Calls to donate can be frontrun adding just-in-time liquidity, with the aim of receiving a portion donated funds.
/// Donors should keep this in mind when designing donation mechanisms.
/// @dev This function donates to in-range LPs at slot0.tick. In certain edge-cases of the swap algorithm, the `sqrtPrice` of
/// a pool can be at the lower boundary of tick `n`, but the `slot0.tick` of the pool is already `n - 1`. In this case a call to
/// `donate` would donate to tick `n - 1` (slot0.tick) not tick `n` (getTickAtSqrtPrice(slot0.sqrtPriceX96)).
```
Fees are donated to uniV4 pool in several listing actions
• liquidateProtectedListing: Amount worth 1ether-listing.tokenTaken-KEEPER_REWARD is donated. This amount will be huge in cases where, someone listed a protected listing and took 0.5 ether as token taken, but did not unlock the listing. So since utilization rate became high, the listing health gone negative and was put to liquidation during this time an amount of (1 ether - 0.5 ether taker - 0.05 ether keeper reward) = 0.40 ether is donated to pool. That's a 1000$ direct donation
• Other 5 flows of Listings contract, such as cancelListing, modifyListings, fillListings, Reserve and Relist donate the tax fees to the pool. The likelihood is above medium to have huge amount when most users do multiple arrays of tokens of multiple collections done in one transaction.
Issue flow:
1. Figure out the tick where the donated fee will go in according to the @notice
2. And provide the in-range liquidity so heavy (like 100x than available in the whole range of that pool).
3. Then do the liquidateProtectedListing, cancelListing, modifyListings, fillListings, Reserve and Relist actions that donate fees worth doing this sandwich
4. Then trigger a fee donation happening on beforeswap hook and then remove the provided liquidity in the first step.
You don't need to frontrun other user's actions, Just do this sandwiching whenever a liquidation of someone's listing happens. And you can also recover the paid tax/fees of your listings by this MEV. Or even better if chain allows to have public mempool, then every user's action is sandwichable.
6835f5ef688c/flayer/src/contracts/implementation/UniswapImplementation.sol#L335-L345
6835f5ef688c/flayer/src/contracts/implementation/BaseImplementation.sol#L58-L62
UniswapImplementation.sol
```
32: /// Prevents fee distribution to Uniswap V4 pools below a certain threshold:
33: /// - Saves wasted calls that would distribute less ETH than gas spent
34: /// - Prevents targetted distribution to sandwich rewards
35: uint public donateThresholdMin = 0.001 ether;
36: >> uint public donateThresholdMax = 0.1 ether;
336: function _distributeFees(PoolKey memory _poolKey) internal {
---- SNIP ----
365:     if (poolFee > 0) {
366:         // Determine whether the currency is flipped to determine which is the donation side
367:         (uint amount0, uint amount1) = poolParams.currencyFlipped ? (uint(0), poolFee) : (poolFee, uint(0));
368:         BalanceDelta delta = poolManager.donate(_poolKey, amount0, amount1, '');
369: 
370:         // Check the native delta amounts that we need to transfer from the contract
371:         if (delta.amount0() < 0) {
372:             _pushTokens(_poolKey.currency0, uint128(-delta.amount0()));
373:         }
374: 
375:         if (delta.amount1() < 0) {
376:             _pushTokens(_poolKey.currency1, uint128(-delta.amount1()));
377:         }
378: 
379:         emit PoolFeesDistributed(poolParams.collection, poolFee, 0);
380:     }
---- SNIP ----
402: }
```
Loss of funds to the LPs. The fees they about to get due to LP, can be sandwiched and extracted. So high severity, and above medium likelihood even in the chains that doesn't have mempool. So, high severity.

## Recommendation
Introduce a new way to track how much is donated on this block and limit it on every _donate call. example, allow only 0.1 ether per block
