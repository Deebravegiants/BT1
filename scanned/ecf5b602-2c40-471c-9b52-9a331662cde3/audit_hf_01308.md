# [M] Incorrect EIP712 typehash

## Summary
Severity: Medium
Contest weight: 0.6817
Dataset id: 6323
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The TYPE_HASH used for EIP712 signing for the order that is signed by the users is incorrect.
According with EIP-712's speciﬁcations, the structs are encoded as follows:
If the struct type references other struct types (and these in turn reference even more struct types), then the set of referenced struct types is collected, sorted by name and appended to the encoding. An example encoding is
Transaction(Person from,Person to,Asset tx)
Asset(address token,uint256 amount)
Person(address wallet,string name)
```solidity
bytes internal constant V3_DUTCH_ORDER_TYPE = abi.encodePacked(
    "V3DutchOrder(",
    "OrderInfo info,",
    "address cosigner,",
    "uint256 startingBaseFee,",
    "V3DutchInput baseInput,",
    "V3DutchOutput[] baseOutputs)"
);
bytes internal constant V3_DUTCH_INPUT_TYPE = abi.encodePacked(
    "V3DutchInput(",
    "address token,",
    "uint256 startAmount,",
    "NonlinearDutchDecay curve,",
    "uint256 maxAmount,",
    "uint256 adjustmentPerGweiBaseFee)"
);
bytes internal constant V3_DUTCH_OUTPUT_TYPE = abi.encodePacked(
    "V3DutchOutput(",
    "address token,",
    "uint256 startAmount,",
    "NonlinearDutchDecay curve,",
    "address recipient,",
    "uint256 minAmount,",
    "uint256 adjustmentPerGweiBaseFee)"
);
bytes internal constant NON_LINEAR_DECAY_TYPE =
    abi.encodePacked(
        "NonlinearDutchDecay(",
        "uint256 relativeBlocks,",
        "int256[] relativeAmounts)"
    );
```
As we can see above, the order should be deﬁned as:
```solidity
abi.encodePacked(V3_DUTCH_ORDER_TYPE, NON_LINEAR_DECAY_TYPE, OrderInfoLib.ORDER_INFO_TYPE, V3_DUTCH_INPUT_TYPE, V3_DUTCH_OUTPUT_TYPE);
```

## Recommendation
```solidity
abi.encodePacked(V3_DUTCH_ORDER_TYPE, NON_LINEAR_DECAY_TYPE, OrderInfoLib.ORDER_INFO_TYPE, V3_DUTCH_INPUT_TYPE, V3_DUTCH_OUTPUT_TYPE);
```
