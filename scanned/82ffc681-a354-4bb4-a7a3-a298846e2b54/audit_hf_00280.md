# [H] `Vault#setController

## Summary
Severity: High
Contest weight: 0.7772
Dataset id: 1430
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function setController(address _controller) public override onlyOwner {
    require(_controller != address(0), "ERROR_ZERO_ADDRESS");

    if (address(controller) != address(0)) {
        controller.migrate(address(_controller));
        controller = IController(_controller);
    } else {
        controller = IController(_controller);
    }

    emit ControllerSet(_controller);
}
```
The owner of the Vault contract can set an arbitrary address as the `controller`.

```solidity
function utilize() external override returns (uint256 _amount) {
    if (keeper != address(0)) {
        require(msg.sender == keeper, "ERROR_NOT_KEEPER");
    }
    _amount = available(); //balance
    if (_amount > 0) {
        IERC20(token).safeTransfer(address(controller), _amount);
        balance -= _amount;
        controller.earn(address(token), _amount);
    }
}
```
A malicious `controller` contract can transfer funds from the Vault to the attacker.

## Proof of Concept
A malicious/compromised can:

  1. Call `Vault#setController()` and set `controller` to a malicious contract;
     * L489 the old controller will transfer funds to the new, malicious controller.
  2. Call `Vault#utilize()` to deposit all the balance in the Vault contract into the malicious controller contract.
  3. Withdraw all the funds from the malicious controller contract.

## Recommendation
Consider disallowing `Vault#setController()` to set a new address if a controller is existing, which terminates the possibility of migrating funds to a specified address provided by the owner. Or, putting a timelock to this function at least.
we assume ownership control is driven safely

Agree with warden that the privilege addresses should not be able to use approvals in a way that rugs users funds.
Based on the fact that we have seen many rug pulls in the space based on compromised “owner” keys, this is a valid attack path. `3 — High: Assets can be stolen/lost/compromised directly (or indirectly if there is a valid attack path that does not have hand-wavy hypotheticals).`
