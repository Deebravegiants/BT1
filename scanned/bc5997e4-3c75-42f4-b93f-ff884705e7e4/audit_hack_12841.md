# [H] Incorrect address for the external TWAP contract will cause a completely DoS to execute DCA Orders

## Summary
Severity: High
Reporter: 0xStalin
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237
Type: audit-issue

## Details
# Incorrect address for the external TWAP contract will cause a completely DoS to execute DCA Orders

## Summary
- The address that is set for the external TWAP contract is incorrect, it is actually an EOA and not a contract account, which will end up causing the whole tx to [execute DCA Orders](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237) to revert
- 
## Vulnerability Detail
- The [address that is set for the external TWAP contract is incorrect](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49), by [checking the TWAP address on arbiscan](https://arbiscan.io/address/0xFa64f316e627aD8360de2476aF0dD9250018CFc5) we can verify that it is actually an EOA and not a contract account.

- Below I describe the different scenarios when interacting with other addresses, and as we can see because the TWAP contract's address is actually an EOA, the tx will revert.
  - If the address is an EOA, the transaction will revert!
  - If the called address has not implemented the called function, the transaction will revert!
  - If the called address has implemented the called function, it will return the value returned by the called function

- **Coded a PoC in remix to demonstrate the above statements**
  - Open Remix & Deploy the 3 contracts, you'll only need to interact with the `Unstoppable::getValue()`.
    - Do the different tests and verify the results:
      - Send the correct address of the `Univ3Twap` contract => You'll get the value that is returned by the `Univ3Twap::getTwap()`
      - Send the address of the `NoFunctionImplemented` contract => The tx will revert because the `getTwap()` is not implemented
      - Send the address of an External Owned Account => The tx will revert

```solidity
pragma solidity 0.8.18;

interface IUniv3Twap {
    function getTwap() external view returns(uint256);
}

contract Unstoppable {
    //@dev -> This function calls a function from a received address
    //@note => If the called address is an EOA, the transaction will revert!
    //@note => If the called address has not implemented the called function, the transaction will revert!
    //@note => If the called address has implemented the called function, it will return the value returned by the called function
    function getValue(address _address) external view returns (uint256 value) {
        value = IUniv3Twap(_address).getTwap();
    }
}

contract Univ3Twap {
    function getTwap() external view returns (uint256 value) {
        value = 100;
    }
}


contract NoFunctionImplemented {
    function randomFunction() external view returns (uint256 value) {
        value = 100;
    }
}
```

- Now that we have verified what happens when calling a function using an EOA address, we can look at the `Dca::execute_dca_order()` and understand why the execution will always revert.
  - When the [`min_amount_out` is computed](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L213) it calls the [`_calc_min_amount_out()`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L255-L276), which will then [call the `TWAP::getTwap()`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268), when this call is made, the tx will be reverted because it will be using an EOA address to call a function.

## Impact
- Full DoS when executing DCA Orders

## Code Snippet
- [Incorrect TWAP contract's address](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49)
- [Calling the getTwap() from the TWAP contract to compute the `min_amount_out` before doing the swap when executing a DCA Order](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268)

## Tool used
Manual Review

## Recommendation
- Make sure to use the correct contract's address for the external TWAP contract to prevent a DoS or computing wrong values.
