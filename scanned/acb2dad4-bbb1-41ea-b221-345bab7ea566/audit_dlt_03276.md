# [M] Centralisation RIsk: `VoterProxy` owner may set the `operate` to an address they own and drain all token balances

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-vetoken
Published: 2022-06-01
Source: https://github.com/code-423n4/2022-05-vetoken-findings/issues/82
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-vetoken/blob/2d7cd1f6780a9bcc8387dea8fecfbd758462c152/contracts/VoterProxy.sol#L274-L285
https://github.com/code-423n4/2022-05-vetoken/blob/2d7cd1f6780a9bcc8387dea8fecfbd758462c152/contracts/VoterProxy.sol#L123-L143


# Vulnerability details

## Impact

The `owner` of `VoterProxy` is able to call `setOperator()` (if the previous operator is shutdown). This allows them to then call `execute()`, `withdraw()` or `withdrawAll()`.  

Execute makes a call to any arbitrary contract with arbitrary data. This may therefore call any ERC20 token, and gauge or the `VoterEscrow` account and withdraw protocol funds.

The functions `withdraw()` and `withdrawAll()` can also be abused to take all funds deposited in the gauges and transfer them to the owner's malicious address.

This poses a significant centralisation risk if the owner private key is compromised or the owner decides to rug pull.

## Proof of Concept

After the owner has updated the `operator` via `setOperator()` they are able to call `VoterProxy.execute()` to execute any call to any smart contract.

```solidity
    function execute(
        address _to,
        uint256 _value,
        bytes calldata _data
    ) external returns (bool, bytes memory) {
        require(msg.sender == operator, "!auth");


        (bool success, bytes memory result) = _to.call{value: _value}(_data);
        require(success, "!success");


        return (success, result);
    }
```

Similarly, for `withdraw()` and `withdrawAll()`
```solidity
    function withdraw(
        address _token,
        address _gauge,
        uint256 _amount
    ) public returns (bool) {
        require(msg.sender == operator, "!auth");
        uint256 _balance = IERC20(_token).balanceOf(address(this));
        if (_balance < _amount) {
            _amount = _withdrawSome(_gauge, _amount.sub(_balance));
            _amount = _amount.add(_balance);
        }
        IERC20(_token).safeTransfer(msg.sender, _amount);
        return true;
    }


    function withdrawAll(address _token, address _gauge) external returns (bool) {
        require(msg.sender == operator, "!auth");
        uint256 amount = balanceOfPool(_gauge).add(IERC20(_token).balanceOf(address(this)));
        withdraw(_token, _gauge, amount);
        return true;
    }
```

## Recommended Mitigation Steps

This issue may be mitigated removing the ability for the `owner` to change the operator in `VoterProxy`.

If the functionality is require ensure it is behind a time lock and multisig / dao.
