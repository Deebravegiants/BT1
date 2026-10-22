# [M] Missing Definition of onlyOwner in HoneyToken

## Summary
Severity: Medium
Contest weight: 0.4254
Dataset id: 12272
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The HoneyFarm protocol provides has the protocol/governance token HoneyToken that will be disseminated to community and protocol users. While examining the HoneyToken contract, we notice the use of a specific modifier onlyOwner, which is not defined yet. To elaborate, we show below the related mint() function, which is designed to allow the privileged owner to mint additional tokens into circulation. However, it comes to our attention that this modifier is not defined.

```solidity
contract HoneyToken is ERC20 {
    uint16 public transferTaxRate = 300;
    uint16 public constant MAXIMUM_TRANSFER_TAX_RATE = 1000;
    address public constant BURN_ADDRESS = 0x000000000000000000000000000000000000dEaD;
    address private _operator;

    event OperatorTransferred(address indexed previousOperator, address indexed newOperator);
    event TransferTaxRateUpdated(address indexed operator, uint256 previousRate, uint256 newRate);

    modifier onlyOperator() {
        require(_operator == msg.sender, "operator: caller is not the operator");
        _;
    }

    constructor() public ERC20("Honey token", "HONEY") {
        _operator = _msgSender();
        emit OperatorTransferred(address(0), _operator);
    }

    function mint(address _to, uint256 _amount) public onlyOwner {
        _mint(_to, _amount);
    }
}
```

## Recommendation
Define the missing onlyOwner or inherit the HoneyToken from the Ownable contract.
