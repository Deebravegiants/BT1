# [H] Malicious Validator Frontrunning Attack

## Summary
Severity: High
Contest weight: 0.6436
Dataset id: 14460
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious validator operator whose validator is about to receive staked ETH from the DepositQueue via the beacon chain deposit contract can front-run the initial deposit to steal the staked ETH.
DepositQueue::stakeETHFromQueue() stakes 32 ETH into a validator on the beacon chain via the DepositContract.
Renzo stakes with trusted third party operators who provide the necessary arguments for the DepositContract::deposit() function for each new validator:
```solidity
function deposit(
    bytes calldata pubkey,
    bytes calldata withdrawal_credentials,
    bytes calldata signature,
    bytes32 deposit_data_root
) override external payable {
```
The withdrawal_credentials parameter sets the address that receives ETH whenever the validator’s beacon chain withdrawals are processed. EigenLayer’s EigenPod contract requires this value to be set as the OperatorDelegator’s assigned EigenPod address. This value can only be set once which occurs when the validator is ﬁrst initialised and receives its ﬁrst ETH deposit from the deposit contract.
Hence, it is possible for a malicious operator to front-run this call with a minimum of 1 ETH to provide their own withdrawal_credentials for the validator. The subsequent 32 ETH deposit from the DepositQueue will still be accepted as a top-up, but the diﬀerent withdrawal_credentials will be ignored by the consensus layer.
Once the 32 ETH deposit has been applied, the malicious operator can withdraw the stake to their own withdrawal credentials address which they provided on their initial 1 ETH deposit.
The impact is rated as high as this allows a malicious node operator to steal 32 ETH from the deposit queue. The likelihood is rated as medium as node operators are partially trusted third parties who control the validator key.

## Recommendation
Each validator’s beacon chain withdrawal credentials should be veriﬁed before ETH is staked into them from the deposit queue.
A minimum of 1 ETH still needs to be deposited for the validator to be initialized, which should be provided by Renzo’s third party operators. Renzo should not be providing the 1 ETH initial deposit as that is also vulnerable to the same front-running attack. Once the withdrawal credentials of that validator has been veriﬁed, Renzo can refund the 1 ETH back to the operators as well as stake the remaining 31 ETH to activate the validator.
Restaking Smart Contract Review
Note that the 31 ETH will have to be staked directly via the deposit contract, as EigenPod::stake() only allows for 32 ETH deposits. Also keep in mind that the OperatorDelegator’s stakedButNotVerifiedEth accounting will also need to be updated to work correctly with the changed validator deposit ﬂow in the recommendation above.
