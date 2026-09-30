# [M] Permanent Fees Loss if The Owner Forgets to Execute the setFeeAddress() Function

## Summary
Severity: Medium
Contest weight: 0.3970
Dataset id: 11357
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FEE_ADDRESS address in PANTHEON.sol contract is used to store 4% tax fees when the user calls mint() or redeem() functions. This 4% fee is distributed as follows:
• 3% will be used to incentivize liquidity providers manually through bribes.
• 1% is the pantheon team profit.
The impact is a loss of liquidity and Pantheon team fees.
In case the owner of the contract forgets to call setFeeAddress() function, FEE_ADDRESS storage variable will be initialized by default to address(0x0). Therefore when someone calls mint() or redeem() functions the fees will be sent to the zero address, which is a loss of tax fees for the protocol.

## Recommendation
It is recommended to pre-set the FEE_ADDRESS in the constructor as follows:
```solidity
- address payable private FEE_ADDRESS;
+ address payable public feeAddress;
+ error ZeroAddressNotAllowed();
constructor(address _feeAddress) payable ERC20("Pantheon", "PANTHEON") {
+ if(_feeAddress == address(0)) revert ZeroAddressNotAllowed();
    _mint(msg.sender, msg.value * MIN);
    totalEth = msg.value;
+ feeAddress = payable(_feeAddress);
    transfer(0x000000000000000000000000000000000000dEaD, 10000);
}
```
