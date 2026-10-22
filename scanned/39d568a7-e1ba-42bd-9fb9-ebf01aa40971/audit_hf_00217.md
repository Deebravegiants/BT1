# [H] Timelock can be bypassed

## Summary
Severity: High
Contest weight: 0.6180
Dataset id: 1123
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The purpose of a Timelock contract is to put a limit on the privileges of the `governor`, by forcing a two step process with a preset delay time.

However, we found that the current implementation actually won’t serve that purpose as it allows the `governor` to execute any transactions without any constraints.

To do that, the current governor can call `Timelock#setGovernor(address _governor)` and set a new `governor` effective immediately.

And the new `governor` can then call `Timelock#setDelay()` and change the delay to `0`, also effective immediately.

The new `governor` can now use all the privileges without a delay, including granting minter role to any address and mint unlimited amount of MALT.

In conclusion, a Timelock contract is supposed to guard the protocol from lost private key or malicious actions. The current implementation won’t fulfill that mission.

```solidity
function setGovernor(address _governor)
    public
    onlyRole(GOVERNOR_ROLE, "Must have timelock role")
{
    _swapRole(_governor, governor, GOVERNOR_ROLE);
    governor = _governor;
    emit NewGovernor(_governor);
}

function setDelay(uint256 _delay)
    public
    onlyRole(GOVERNOR_ROLE, "Must have timelock role")
{
    require(
        _delay >= 0 && _delay < gracePeriod,
        "Timelock::setDelay: Delay must not be greater equal to zero and less than gracePeriod"
    );
    delay = _delay;

    emit NewDelay(delay);
}
```

## Recommendation
Consider making `setGovernor` and `setDelay` only callable from the Timelock contract itself.

Specificaly, changing from `onlyRole(GOVERNOR_ROLE, "Must have timelock role")` to `require(msg.sender == address(this), "...")`.

Also, consider changing `_adminSetup(_admin)` in `Timelock#initialize()` to `_adminSetup(address(this))`, so that all roles are managed by the timelock itself as well.

The warden has identified an exploit that allows to sidestep the delay for the timelock, effectively bypassing all of the timelock’s security guarantees. Because of the gravity of this, I agree with the high risk severity.

Mitigation can be achieved by ensuring that all operations run under a time delay
