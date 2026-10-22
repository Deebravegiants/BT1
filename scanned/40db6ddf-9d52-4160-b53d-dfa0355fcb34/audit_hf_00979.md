# [M] `OperateProxy.callFunction

## Summary
Severity: Medium
Contest weight: 0.2490
Dataset id: 3063
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Controller.sol#L550-L558](https://github.com/code-423n4/2022-03-rolla/blob/efe4a3c1af8d77c5dfb5ba110c3507e67a061bdd/quant-protocol/contracts/Controller.sol#L550-L558)  

        /// @notice Allows a sender/signer to make external calls to any other contract.
        /// @dev A separate OperateProxy contract is used to make the external calls so
        /// that the Controller, which holds funds and has special privileges in the Quant
        /// Protocol, is never the `msg.sender` in any of those external calls.
        /// @param _callee The address of the contract to be called.
        /// @param _data The calldata to be sent to the contract.
        function _call(address _callee, bytes memory _data) internal {
            IOperateProxy(operateProxy).callFunction(_callee, _data);
        }

[OperateProxy.sol#L10-L19](https://github.com/code-423n4/2022-03-rolla/blob/efe4a3c1af8d77c5dfb5ba110c3507e67a061bdd/quant-protocol/contracts/utils/OperateProxy.sol#L10-L19)  

        function callFunction(address callee, bytes memory data) external override {
            require(
                callee != address(0),
                "OperateProxy: cannot make function calls to the zero address"
            );

            (bool success, bytes memory returnData) = address(callee).call(data);
            require(success, "OperateProxy: low-level call failed");
            emit FunctionCallExecuted(tx.origin, returnData);
        }

As the `OperateProxy.sol#callFunction()` function not payable, we believe it’s not the desired behavior to call a non-contract address and consider it a successful call.

For example, if a certain business logic requires a successful `token.transferFrom()` call to be made with the `OperateProxy`, if the `token` is not a existing contract, the call will return `success: true` instead of `success: false` and break the caller’s assumption and potentially malfunction features or even cause fund loss to users.

The qBridge exploit (January 2022) was caused by a similar issue.

As a reference, OpenZeppelin’s `Address.functionCall()` will check and `require(isContract(target), "Address: call to non-contract");`

        function functionCallWithValue(
            address target,
            bytes memory data,
            uint256 value,
            string memory errorMessage
        ) internal returns (bytes memory) {
            require(address(this).balance >= value, "Address: insufficient balance for call");
            require(isContract(target), "Address: call to non-contract");

            (bool success, bytes memory returndata) = target.call{value: value}(data);
            return verifyCallResult(success, returndata, errorMessage);
        }

        function isContract(address account) internal view returns (bool) {
            // This method relies on extcodesize/address.code.length, which returns 0
            // for contracts in construction, since the code is only stored at the end
            // of the constructor execution.

            return account.code.length > 0;
        }

## Recommendation
Consider adding a check and throw when the `callee` is not a contract.

Resolved in [RollaProject/quant-protocol#85](https://github.com/RollaProject/quant-protocol/pull/85).
