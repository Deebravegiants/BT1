# [M] Sandwiched register() And transferLEND() For Airdrop

## Summary
Severity: Medium
Contest weight: 0.4140
Dataset id: 13199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LEND by TEN Finance protocol, the Airdrop contract allows the investor to register the airdrop and transfer the airdrop rewards every 90 days. To get the qualification for the airdrop, the protocol requires the user to have a minimum balance of tenfi in the holding account. While examining this part of logic, we notice an issue in current implementation. To elaborate, we show below the related routines.
```solidity
function register() external nonReentrant {
    require(block.timestamp < airdropStartTime, "Registration time already ended");
    address user = _msgSender();
    uint256 tenfi_amount = getUserTenfiBalance(user);
    require(tenfi_amount >= MIN_QUALIFY_AMOUNT, "Insufficient tenfi balance qualify");

    function getUserTenfiBalance(address user) public view returns(uint tenfi_bal) {
        address _tenfiAddress = TENFI_ADDRESS; // gas-savings
        // User wallet tenfi balance
        tenfi_bal += IERC20(_tenfiAddress).balanceOf(user);
        uint256 tenfi_farm_length = registeredTenfiFarmVaultsId.length;
    }
}

function transferLEND() external nonReentrant {
    *if user
```

## Recommendation
Take into account the tenfi staked time as well for airdrop qualification.
