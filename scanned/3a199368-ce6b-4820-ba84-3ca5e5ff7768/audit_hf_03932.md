# [H] Oracle request timestamp and pending posi- tions mismatch

## Summary
Severity: High
Contest weight: 0.6425
Dataset id: 20249
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An example of what happens exactly:
1. PythOracle granularity is set to 100.
2. User opens position at timestamp = 101. Pending position is stored with timestamp = 200 (because PythOracle returns currentTimestamp = 200)
3. At the same time oracle.request() is called, which stores 101 (current timestamp) into versionList
4. User calls oracle.commitRequested(), which stores current price into _prices[101]
5. Later when that pending position is settled, it requests oracle.at(200) which doesn't have a price set (is invalid).
The same will happen to all pending positions - so most of them will easily be invalid, which will completely break the protocol and cause all kinds of problems due to pending positions being invalid and not updating profit and loss properly.
The most straightforward impact is unexpectedly long position commit times and possible funds loss due to this, if the oracle commit flow is the normal expected flow (only commit requested versions). For example: T=1: User A requests to open position long = 1. Position timestamp = 100. Oracle request timestamp = 1 T=15: Oracle commits requested version at timestamp = 1, price = $100. T=10010: User B requests to open position. Position timestamp = 10100. Oracle request timestamp = 10010 T=10025: Oracle commits requested version at timestamp = 10010, price = $110.
User A expects to be filled at price close to $100. However, he's only filled when the next user trades after him, which happens much later than expected with a very different price ($110), so User A has lost $10 unexpectedly. Basically, each user will only be settled when the next user trades. In quiet markets this can lead to very long settlement times and very bad prices for users.
User A, however, can notice these long waiting times and can fix it by voluntary commiting non-requested versions. For example, he can commit at T=120 and be filled with the correct price. However, this will mean that all commits must be made non-requested, thus they will not be rewarded with the keeper fees. So the user will pay keeper fees when trading, but will also be forced to lose gas fees for oracle commits, so either broken and long waiting times, or broken oracle non-rewarded updates: both are high impacts.
Another impact is completely broken internal accounting due to a lot of invalid oracle versions. There is a different bug reported by me about desync of global and local positions during invalid oracles. This bug, when coupled with the desync of global and local positions, will lead to catastrophic consequences and complete breakage of accounting of collateral, bank run and loss of funds for users. Scenario of what can (and will) happen: User B has active open position maker=2 with collateral = 100 T=99: User A opens long=1 with collateral=100: update(0,1,0,100) (pending position timestamp = 100) T=101: User A decides to close: update(0,0,0,0) (pending position timestamp = 200) T=130: Oracle commited for timestamp=110, price = $100 (user A position at timestamp = 100 is invalid) T=150: User B settles: update(2,0,0,0) T=220: Oracle commited for timestamp=205, price = $90 after settlement of user A and user B: user A will have collateral = $100 (local pending position long = 1 at timestamp = 100 will be invalidated and ignored) user B will have collateral = $110 (global pending position long = 1 will be current at timestamp 110 and accumulate pnl from timestamp 110 to timestamp=205)
So total deposit of both users is $100 + $100 = $200 Total collateral in the end: $100 + $110 = $210 But protocol only has $200 in funds, so users will be unable to withdraw everything, which can cause bank run and loss of funds for the last user.
Such situations will happen all the time by themselves due to lots of invalid oracle versions, so this will mess up accounting completely.

## Recommendation
Make timestamp of pending positions and timestamp of oracle request match.
Record current() as a timestamp for the request():
```solidity
function request(address) external onlyAuthorized {
    uint nextTimestamp = current();
    if (versionList.length == 0 || versionList[versionList.length - 1] < nextTimestamp) {
        versionList.push(nextTimestamp);
    }
}
```
