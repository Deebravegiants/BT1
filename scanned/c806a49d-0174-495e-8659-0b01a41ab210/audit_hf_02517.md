# [M] Potential Reentrancy Risk in xtoken Repayment

## Summary
Severity: Medium
Contest weight: 0.4640
Dataset id: 13428
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in smart contract development is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [12] exploit, and the recent Uniswap/Lendf.Me hack [11].

We notice there are occasions where the checks-effects-interactions principle is violated. Using the xtoken as an example, the _repay_internal() function (see the code snippet below) is provided to externally call a token contract to transfer assets (as repayment). However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. For example, the interaction with the external contract (line 1180) start before effecting the update on internal states (lines 1185-1186), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the same entry function.

```solidity
func _repay_internal{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    _payer : felt, _borrower : felt, _repay_amount : Uint256) -> (
    actual_repay_amount : Uint256):
    alloc_locals
    accrue_interest()
    let (local total_borrows) = total_borrows.read()
    let (local xcontroller) = xcontroller.read()
    let (local self) = get_contract_address()
    let (local borrow_index) = borrow_index.read()
    # validate based on xcontroller validation rules
    let (_is_repay_allowed) = IXcontroller.repay_allowed(
        xcontroller, self, _payer, _borrower, _repay_amount)
    assert _is_repay_allowed = 1
    # check repay amount > 0
    let (_is_repay_amount_gt_zero) = uint256_lt(Uint256(0, 0), _repay_amount)
    assert _is_repay_amount_gt_zero = 1
    # get the recent borrow balance (principal) + accrued interest of the _borrower
    let (_recent_borrow_balance) = _borrow_balance_stored_internal(_borrower)
    let (_is_borrow_balance_gt_zero) = uint256_lt(Uint256(0, 0), _recent_borrow_balance)
    assert _is_borrow_balance_gt_zero = 1
    # check _safe_repay_amount so payer won't overpay the debt
    let (_safe_repay_amount) = _get_safe_repay_amount(_repay_amount, _recent_borrow_balance)
    # transfer from payer to this contract
    let (_actual_repay_amount) = _do_transfer_in(_payer, _safe_repay_amount)
    # update total_borrows and account_borrows
    let (_updated_borrow_balance) = uint256_sub(_recent_borrow_balance, _actual_repay_amount)
    let (_updated_total_borrows) = uint256_sub(total_borrows, _actual_repay_amount)
    total_borrows.write(_updated_total_borrows)
    account_borrows.write(
        _borrower, BorrowSnapshot(principal= _updated_borrow_balance, interest_index= borrow_index))
    log_repay.emit(
        payer=_payer,
        borrower=_borrower,
        repay_amount=_actual_repay_amount,
        account_borrow_balance=_updated_borrow_balance,
        total_borrows=_updated_total_borrows,
        borrow_index=borrow_index)
    return (actual_repay_amount=_actual_repay_amount)
end
```

While the supported tokens in the protocol do implement rather standard ERC20 interfaces and their related token contracts are not vulnerable or exploitable for re-entrancy, it is important to take precautions to thwart possible re-entrancy. And the adherence of the checks-effects-interactions best practice is strongly recommended.

From another perspective, the traditional mitigation in applying money-market-level reentrancy protection can be strengthened by elevating the reentrancy protection at the xcontroller-level. In addition, each individual function can be self-strengthened by following the checks-effects-interactions principle.

## Recommendation
Apply necessary reentrancy prevention by following the checks-effects-interactions principle and utilizing the necessary nonReentrant modifier to block possible re-entrancy. Also consider strengthening the reentrancy protection at the protocol-level instead of at the current money-market granularity.
