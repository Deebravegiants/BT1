# [H] _calc_min_amount_out is ieffective in execute_dca_order function and exposes user to unlimited slippage and user funds can be drained,

## Summary
Severity: High
Reporter: BugBusters
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L215-L222
Type: audit-issue

## Details
# _calc_min_amount_out is ieffective in execute_dca_order function and exposes user to unlimited slippage and user funds can be drained,

## Summary
_calc_min_amount_out is ieffective in execute_dca_order function and exposes user to unlimited slippage, as execute_dca function is callable by anyone.
## Vulnerability Detail
Anyone can call the `execute_dca` function in the Dca.vy passing its own arguments but the problem is that :
1. In uniswap v3 an attacker can create a pool with ultra low liquidity and maintain the TWAP price of his own for certain length of time, that should not be hard and even easier on arbitrum.
2. Attacker will call the execute_dca_order function with his own pool path.
3. `_calc_min_amount_out` will be called with the passed arguments and price will be calculated wrong and will expose the user to unnecessary unlimited slippage and snadwich attacks. 

Also another case could be 

1. User pass his own path with very high price.
2. Assets are swapped at the following line for very high price:
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L215-L222
3. User is wrecked.

For more reference check the following issue in splits Sherlock competition:
(https://github.com/sherlock-audit/2023-04-splits-judging#issue-m-3-tokens-without-univ3-pairs-with-tokentobeneficiary-can-be-stolen-by-an-attacker) [Splits Uniswap vulnerability]

## Impact
Exposed to unlimited slippage or user funds can be drained.
## Code Snippet
```solidity
def execute_dca_order(_uid: bytes32, _uni_hop_path: DynArray[address, 3], _uni_pool_fees: DynArray[uint24, 2], _share_profit: bool):
    assert not self.is_paused, "paused"

    order: DcaOrder = self.dca_orders[_uid]
    
    # validate
    assert order.number_of_executions < order.max_number_of_executions, "max executions completed"
    assert order.last_execution + order.seconds_between_executions < block.timestamp, "too soon"

    # ensure path is valid
    assert len(_uni_hop_path) in [2, 3], "[path] invlid path"
    assert len(_uni_pool_fees) == len(_uni_hop_path)-1, "[path] invalid fees"
    assert _uni_hop_path[0] == order.token_in, "[path] invalid token_in"
    assert _uni_hop_path[len(_uni_hop_path)-1] == order.token_out, "[path] invalid token_out"

    # effects
    order.last_execution = block.timestamp
    order.number_of_executions += 1

    self.dca_orders[_uid] = order

    # ensure user has enough token_in
    account_balance: uint256 = ERC20(order.token_in).balanceOf(order.account)
    if account_balance < order.amount_in_per_execution:
        log DcaOrderFailed(_uid, order.account, "insufficient balance")
        self._cancel_dca_order(_uid, "insufficient balance")
        return

    # ensure self has enough allowance to spend amount token_in
    account_allowance: uint256 = ERC20(order.token_in).allowance(order.account, self)
    if account_allowance < order.amount_in_per_execution:
        log DcaOrderFailed(_uid, order.account, "insufficient allowance")
        self._cancel_dca_order(_uid, "insufficient allowance")
        return

    # transfer token_in from user to self
    self._safe_transfer_from(order.token_in, order.account, self, order.amount_in_per_execution)

    # approve UNISWAP_ROUTER to spend amount token_in
    ERC20(order.token_in).approve(UNISWAP_ROUTER, order.amount_in_per_execution)

    # Vyper way to accommodate abi.encode_packed
    path: Bytes[66] = empty(Bytes[66])
    if(len(_uni_hop_path) == 2):
        path = concat(convert(_uni_hop_path[0], bytes20), convert(_uni_pool_fees[0], bytes3), convert(_uni_hop_path[1], bytes20))
    elif(len(_uni_hop_path) == 3):
        path = concat(convert(_uni_hop_path[0], bytes20), convert(_uni_pool_fees[0], bytes3), convert(_uni_hop_path[1], bytes20), convert(_uni_pool_fees[1], bytes3), convert(_uni_hop_path[2], bytes20))
    
    min_amount_out: uint256 = self._calc_min_amount_out(order.amount_in_per_execution, _uni_hop_path, _uni_pool_fees, order.twap_length, order.max_slippage)

    uni_params: ExactInputParams = ExactInputParams({
        path: path,
        recipient: self,
        deadline: block.timestamp,
        amountIn: order.amount_in_per_execution,
        amountOutMinimum: min_amount_out
    })
    amount_out: uint256 = UniswapV3SwapRouter(UNISWAP_ROUTER).exactInput(uni_params)

    # transfer amount_out - fee to user 
    amount_minus_fee: uint256 = amount_out * (FEE_BASE - self.fee) / FEE_BASE
    self._safe_transfer(order.token_out, order.account, amount_minus_fee)

    # allows searchers to execute for 50% of profits
    if _share_profit:
        profit: uint256 = amount_out - amount_minus_fee
        self._safe_transfer(order.token_out, msg.sender, profit/2)
    
    log DcaOrderExecuted(_uid, order.account, order.number_of_executions, order.amount_in_per_execution, amount_minus_fee)

    if order.number_of_executions == order.max_number_of_executions:
        self._cleanup_order(_uid)
        log DcaCompleted(_uid, order.account)
```
## Tool used

Manual Review

## Recommendation
This function should not be public or there should be liquidity checks when performing swaps on uniswap.
