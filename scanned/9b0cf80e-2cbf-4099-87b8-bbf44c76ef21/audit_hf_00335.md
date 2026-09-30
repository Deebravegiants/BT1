# [M] `permitAndMulticall`

## Summary
Severity: Medium
Contest weight: 0.4888
Dataset id: 1646
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the `_from` address is not the `msg.sender` `_multiCall()` will be made on behalf of the `msg.sender`. As a result each of the functions called by `multiCall()` will be made on behalf of `msg.sender` and not `_from`.

If functions such as `transfer()` or `unstake()` are called `msg.sender` will be the original caller which would transfer the attacker the funds if the `to` field is set to an attackers address.

Furthermore, if an attacker we to call `permitAndMulticall()` before the `_from` user they may use their signature and nonce combination. As a nonce is only allowe to be used once the siganture will no longer be valid and `_permitToken.permit()` will fail on the second call.

An attacker may use this as a Denial of Service (DoS) attack by continually front-running `permitAndCall()` using other users signatures.

## Proof of Concept
```solidity
function _multicall(bytes[] calldata _data) internal virtual returns (bytes[] memory results) {
  results = new bytes[](_data.length);
  for (uint256 i = 0; i < _data.length; i++) {
    results[i] = Address.functionDelegateCall(address(this), _data[i]);
  }
  return results;
}

function _permitAndMulticall(
  IERC20Permit _permitToken,
  address _from,
  uint256 _amount,
  Signature calldata _permitSignature,
  bytes[] calldata _data
) internal {
  _permitToken.permit(
    _from,
    address(this),
    _amount,
    _permitSignature.deadline,
    _permitSignature.v,
    _permitSignature.r,
    _permitSignature.s
  );

  _multicall(_data);
}
```

## Recommendation
Consider updating the `_from` field to be the `msg.sender` in `permitAndMulticall()` (or alternatively do this in `_permitAndMulticall()` to save some gas).
    
    function permitAndMulticall(
      uint256 _amount,
      Signature calldata _permitSignature,
      bytes[] calldata _data
    ) external {
      _permitAndMulticall(IERC20Permit(address(ticket)), msg.sender, _amount, _permitSignature, _data);
    }

PR: <https://github.com/pooltogether/v4-twab-delegator/pull/29>

Should be labelled as a 3 (High Risk) issue because an attacker could steal the funds.

I’m not exactly sure how this might be abused to steal funds. By front-running a call `permitAndMulticall()` with the same `_from` account, an attacker is able to use up the user’s nonce and DoS their transactions. However, an attacker CAN control the `_data` parsed to the `_multicall()` function and delegate call to the `TWABDelegator.sol` contract. Although, in this case `msg.sender` will be the attacker and not the delegatee.
 
As such, any call to transfer a delegation to another account will fail as the delegation is computed based off `msg.sender` and `_slot`.
 
Could you confirm if there is a viable attack vector that would result in lost funds? @PierrickGT 

You are right, the only attack vector possible would be with the `updateDelegatee` function since an attacker could pass a `_delegatee` address and we compute the delegation with the passed `_delegator` param. <https://github.com/pooltogether/v4-twab-delegator/blob/60ae14e11947f8c896c1fef8f4d19ee714719383/contracts/TWABDelegator.sol#L265>
 
Funds wouldn’t be at risk but delegated to the attacker address. So I think the `2 (Med Risk)` label makes sense in this case since funds are not directly at risk but the attacker would enjoy better odds of winning. I’ve removed the `disagree with severity` label.

As per the above comment, I will leave this as `2 (Med Risk)`. The exploit does not lead to a loss of funds but can be abused to DoS this functionality and enjoy better odds of winning.
