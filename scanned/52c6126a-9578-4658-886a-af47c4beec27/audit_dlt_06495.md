# [M] `LM_PC_Staking_v1` can be used for pyramid scheme, because it is using current stakers funds to reward others

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-08
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/70
Type: hats-finding

## Details
**Github username:** @NicolaMirchev
**Twitter username:** EgisSec
**Submission hash (on-chain):** 0x6ecbce60bcd9552924e1d97a4071d452c97d7300d0fe3cf05a4625e452e0af95
**Severity:** medium

**Description:**
**Description**\
[LM_PC_Staking_v1](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/62892384fd7d0ce4d0e389c530200c69921473f7/src/modules/logicModule/LM_PC_Staking_v1.sol#L41-L44) is inheriting from `ERC20PaymentClientBase_v1`, which means it is treated as a regular `paymentClient` module, but this is not correct approach, because in the case of staking, end users are providing their funds, which are used for incentivising other stakers. (Users play the role of a funding manager). And only when staking contract balance doesn't have the funds for given operation, it would try to pull funds from `FundingManager` contract. But there is no guarantee that the funding manager would be funded, which would result in an expoit of type `pull-rug` + `pyramid`. If a malicious party has noticed that contract functionality is using stakers funds to incetives other stakers, he can create a staking contract with very attractive `rewardRate` and `rewardToken`, which would attract users and last ones to try getting their funds back would be deceived.
The problem is that every time a user interact with the contract `stake/unstake`, his recurred rewards are being processed and sent to him in a way that uses other stakers rewards:
We start from `_distributeRewards`
```
        _addPaymentOrder(
            PaymentOrder({
                recipient: recipient,
                paymentToken: address(orchestrator().fundingManager().token()),
                amount: amount,
                start: block.timestamp,
                cliff: 0,
                end: block.timestamp
            })
        );

        __Module_orchestrator.paymentProcessor().processPayments(
            IERC20PaymentClientBase_v1(address(this))
        );
```
here we call [paymentProcessor::processPayments](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/62892384fd7d0ce4d0e389c530200c69921473f7/src/modules/paymentProcessor/PP_Simple_v1.sol#L97) , than back to staking contract -> [ERC20PaymentClientBase_v1::collectPaymentOrders](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/62892384fd7d0ce4d0e389c530200c69921473f7/src/modules/logicModule/abstracts/ERC20PaymentClientBase_v1.sol#L144). This function will check if current contract (staking) [have enough funds to distribute to recipients](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/62892384fd7d0ce4d0e389c530200c69921473f7/src/modules/logicModule/abstracts/ERC20PaymentClientBase_v1.sol#L248-L276). Most of the time, this would be the case, because this is the contract, where user funds are staying.


**Attack Scenario**\
- An expliter has notices the issue that staking contract is using `paymentClient` direct logic, which in terms of staking is practically rug-pull weapon
- He creates an orchestrator and module trough the protocol  and set very attractive reward rate of 20% APR for ethereum. 
- There would be many victims, which would see that, especially if Inverter would have a place to look for projects, which have been deployed using their framework
- The system will work great in the beginning and the expoiter himself may open a large stake position for himself, which would later benefit from his followers
- In some point users will start unstaking, which would be okay, untill all funds are withdrawn from the protocol (some of them for incetivicing other users)
- Last users to unstake would have lost their funds

**Attachments**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/70_
