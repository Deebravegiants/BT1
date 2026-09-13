# [M] `delegate()` function would fail as the minimum delegation amount as per Oasis is 100 ROSE

## Summary
Severity: Medium
Chain: Smart contract
Component: Accumulated-finance
Published: 2024-09-02
Source: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/4
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xac46fe1d6e99890065fd4f3b1b922a2cbaec59fb670e7c9c05d9a872b60b6aac
**Severity:** medium

**Description:**
**Description**\
`stROSEMinter.sol` has `delegate()` function which is used to delegate the ROSE tokens to the staking address of validator on the consensus layer. The function checks, the amount passed is greater than 0.


```solidity
    function delegate(StakingAddress to, uint128 amount) public onlyOwner returns (uint64) {
        require(amount < type(uint128).max, ">MaxUint128");
@>      require(amount > 0, "ZeroDelegate");
        uint64 receiptId = nextReceiptId++;
        Subcall.consensusDelegate(to, amount, receiptId);
        delegationReceipts[receiptId] = DelegationReceipt({
            exists: true,
            to: to,
            blockNumber: block.number,
            receiptTaken: false,
            receiptTakenBlockNumber: 0,
            shares: 0,
            amount: amount
        });
        emit Delegate(to, amount, receiptId);
        return receiptId;
    }
```

The issue is that, it breaks the intended minimum delegation amount by OASIS which is set as 100 ROSE tokens currently. The documentation explicitely states that:

> The minimum amount of tokens one can delegate. The value is set to 100,000,000,000 base units, or 100 ROSE tokens.

This design constraint is not implemented in `delegate()` function which allows any amount to be passed by user to staking address on consensus layer. The delegation will fail if the minimum per-validator amount has not been reached 100 ROSE tokens. The malicious user can repeat this by delegating 1 ROSE tokens to staking address with the intent to harm otehr users intending to delegate their tokens by continuosly sending the transactions to oasis chain. 

**Recommendations**\
Add validation check, minimum delegation amount by OASIS i.e 100 ROSE tokens must be checked. Only allow delegations for minimum 100 ROSE tokens.
