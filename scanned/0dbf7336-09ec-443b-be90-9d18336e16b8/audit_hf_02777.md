# [M] Insufficient Gas For receiveToken()

## Summary
Severity: Medium
Contest weight: 0.4487
Dataset id: 15174
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When sending tokens to a bridge with a lockbox, 180_000 gas is given to the receiveToken() function. However, this
is insufficient in certain scenarios. Specifically, this is insufficient in cases where the try statement in _receiveToken()
fails at the last possible moment and the catch-body has to be executed even though a lot of gas has already been
consumed.
For example, when the test test_receiveToken_succeeds_insolvent_lockbox is modified to use a 180_000 gas stipend,
it will revert since there was not enough gas remaining to execute the catch-body. A similar scenario where gas may
run out is if the underlying token has paused transfers.
In case receiveToken() runs out of gas, the cross chain call fails and can not be retried, meaning that the tokens for
this transfer are lost.
```solidity
Bridge.sol
function _receiveToken(address to, uint256 value) internal {
    // Cache addresses for gas optimization.
    address _token = token;
    address _lockbox = lockbox;
    if (_lockbox == address(0)) {
        // If no lockbox is set, just mint the wrapped tokens to the recipient.
        ITokenOps(_token).mint(to, value);
    } else {
        // If a lockbox is set, mint the wrapped tokens to the bridge contract.
        ITokenOps(_token).mint(address(this), value);
        // Attempt withdrawal from the lockbox, but transfer the wrapped tokens to the recipient if it fails.
        try ILockbox(_lockbox).withdrawTo(to, value) { }
        catch {
            _token.safeTransfer(to, value);
            emit LockboxWithdrawalFailed(_lockbox, to, value);
        }
    }
    emit TokenReceived(xmsg.sourceChainId, to, value);
}
```

## Recommendation
Consider increasing the gas stipend. Keep in mind that different token implementations will consume different amounts
of gas. Additionally, different chains may implement different gas pricing for opcodes, and future chain upgrades may
also change opcode pricing. As such, it may be useful to implement mechanisms that allow an admin to change the gas
stipends.
rlUSD Bridge Contract
