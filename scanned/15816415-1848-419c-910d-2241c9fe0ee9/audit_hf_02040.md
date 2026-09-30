# [H] Suggested Adherence Of Checks-Effects-Interactions Pattern

## Summary
Severity: High
Contest weight: 0.6365
Dataset id: 11630
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle.
This principle is effective in mitigating a serious attack vector known as re-entrancy.
Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner.
Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once.
This attack was part of several most prominent hacks in Ethereum history, including the DAO [16] exploit, and the recent Uniswap/Lendf.Me hack [15].
We notice there are several occasions where the checks-effects-interactions principle is violated.
Using the D_Swap as an example, the Impl_Delivery() function (see the code snippet below) is provided to externally call a token contract to transfer assets.
However, the invocation of an external contract requires extra care in avoiding the above re-entrancy.
Apparently, the interactions with the external contract (line 366) start before effecting the update on the internal state (line 370), hence violating the principle.
In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the same entry function.
```solidity
function Impl_Delivery(address user) internal {
    uint256 head_amount_back = m_Future_Balance_Tail[user];
    if(head_amount_back >= 1)
        Charging_Transfer_ERC20(m_Token_Head, user, head_amount_back);
    m_Amount_Head_Deliveryed = m_Amount_Head_Deliveryed.add(head_amount_back);
    m_Total_Future_Balance_Tail = m_Total_Future_Balance_Tail.sub(head_amount_back);
    m_Future_Balance_Tail[user] = 0;
    uint256 tail_amount_back = 0;
    tail_amount_back = m_Future_Balance_Head;
    m_Future_Balance_Head = 0;
    Charging_Transfer_ERC20(m_Token_Tail, owner, tail_amount_back);
    m_Amount_Tail_Deliveryed += tail_amount_back;
    D_Swap_Main(m_DSwap_Main_Address).Triger_Claim_For_Delivery(address(this), user);
}
```
Note that other routine Deposit_For_Tail() shares the same issue.

## Recommendation
Apply necessary reentrancy prevention by utilizing the nonReentrant modifier to block possible re-entrancy.
