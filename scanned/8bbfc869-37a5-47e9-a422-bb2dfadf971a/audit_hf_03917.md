# [M] Faulty interest calculations force agents to

## Summary
Severity: Medium
Contest weight: 0.4623
Dataset id: 20217
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Agents can be made to overpay due to faulty interest calculations. The function borrow() is used by agents to borrow FIL tokens and the function pay() is used to pay down their debt. Agents are allowed to increase the amount they have borrowed as long as their accounts are healthy. The interest calculated on borrows is tracked by the variable account.epochsPaid, which tracks the last block.number for which the interest has been paid. The interest is calculated as interest = (principal * (block.number - account.epochsPaid) * interestRate) and the decimals are adjusted. The problem is that if an agent borrows, then borrows again before paying, the interest is calculated on the new principal, but the account.epochsPaid is not updated. This means that the interest is calculated on the new principal from the last paid block. This can be used to force Agents to overpay interest. The main issue is that when a borrow() is called, the account's epochsPaid is not updated. This is evident by looking at the code snippet for the same function. ool.sol#L312-L340 The bug can be reproduced by the following steps:
1. Alice borrows 1 FIL token. the rate of interest is 18% per year. Her account.epochsPaid is set to the current block number. Let's assume Alice is required to pay the interest only once a year.
2. After a year, right before paying interest, Alice borrows another 1 FIL token. She then repays her whole debt.
3. Theoretically, according to the specifications of the protocol, Alice is required to pay 18% on the first FIL tokens she borrowed, and no interest or very little interest on the next FIL token since that loan is closed in the very next block. Thus the effective interest rate would be 18% of 1e18 FIL tokens = 1.8e17 FIL tokens.
4. Practically, on the second borrow the account.principal gets bumped to 2e18 FIL tokens. epochsPaid isn't updated. Thus Alice's interest is calculated as 18% of the principal for 1 year, thus 18% of 2e18 FIL tokens = 3.6e17 FIL tokens. This is double the amount of interest Alice should have paid!
Agents will be forced to pay more interest than necessary due to faulty interest calculations. A POC is provided to demonstrate the bug. The POC is a fork of the original test suite. The POC demonstrates the following steps:
1. Scenario #1: Agent borrows an amount, and pays it off entirely after 100 blocks. The interest amount sent to the treasury is recorded. The interest values are then reset in the pool.
2. Scenario #2: Agent borrows the same amount for the same duration. Then the Agent borrows the same amount again and immediately closes the position. The interest amount sent to the treasury is recorded again.
3. According to normal loaning protocols, the interest in both scenarios should be almost the same since the second loan is held for only 1 block. But the POC demonstrates that the interest charged in the second scenario is more than twice that of the first. This is because the interest is calculated on the new principal, but the account.epochsPaid is not updated.
```solidity
function testAttackOverpay() public {
    emit log_string("Scenario 1");
    uint256 amount = WAD;
    // Scenario 1
    agentBorrow(
        agent,
        poolID,
        issueGenericBorrowCred(agentID, borrowAmount)
    );
    vm.roll(block.number + 100);
    Account memory account = AccountHelpers.getAccount(
        router,
        address(agent),
        poolID
    );
    emit log_named_uint(
        "Interest blocks",
        block.number - account.epochsPaid
    );
    emit log_named_uint("Principal", account.principal);
    agentPay(agent, pool, issueGenericPayCred(agentID, 10 * amount));
    uint256 feesCollected = pool.feesCollected();
    pool.harvestFees(feesCollected);
    emit log_named_uint("feesCollected", feesCollected);
    // Scenario 2
    emit log_string("Scenario 2");
    agentBorrow(
        agent,
        poolID,
        issueGenericBorrowCred(agentID, borrowAmount)
    );
    vm.roll(block.number + 100);
    agentBorrow(
        agent,
        poolID,
        issueGenericBorrowCred(agentID, borrowAmount)
    );
    account = AccountHelpers.getAccount(router, address(agent), poolID);
    emit log_named_uint(
        "Interest blocks",
        block.number - account.epochsPaid
    );
    emit log_named_uint("Principal", account.principal);
    agentPay(agent, pool, issueGenericPayCred(agentID, 10 * amount));
    feesCollected = pool.feesCollected();
    pool.harvestFees(feesCollected);
    emit log_named_uint("feesCollected", feesCollected);
}
```
Terminal output: Running 1 test for test/Pool.t.sol:PoolFeeTests [PASS] testAttackOverpay() (gas: 1181925) Logs: Scenario 1 Interest blocks: 100 Principal: 1000000000000000000 feesCollected: 2113774733638 Scenario 2 Interest blocks: 101 Principal: 2000000000000000000 feesCollected: 4269406392695

## Recommendation
Record the owed interest and then update account.epochsPaid to the current block number once borrow() is called. This would prevent the interest from being calculated on the new principal from the past paid block.
