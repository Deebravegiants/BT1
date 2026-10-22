# [M] Deposit function can be DOSed

## Summary
Severity: Medium
Contest weight: 0.4587
Dataset id: 14907
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deposit function requires that the sum of fixed and variable deposits be strictly equal to the fixedSideCapacity and variableSideCapacity correspondingly. This is done by checking the supply of deposit tokens and current msg.value (L395 and L409). But if the msg.value is bigger than the difference between the total supply of deposit tokens and side capacity - the whole deposit tx would be reverted. This opens a griefing attack vector when malicious actors could DOS deposit function. Since the vault is permissionless - an attacker could spot users' tx that would start the vault and front-run it with a dust amount deposit, causing reverting of the first one. This could be repeated many times, effectively preventing the vault from being started.
File: LidoVault.sol
```solidity
function deposit(uint256 side) external payable isInitialized nonReentrant {
    require(!isStarted(), "DAS");
    // don't allow deposits once settle debt process has been initialized to prevent vault from starting
    require(!isAdminSettleDebtInitialized(), "AAI");
    require(side == FIXED || side == VARIABLE, "IS");
    require(msg.value > 0, "NZV");

    uint256 amount = msg.value;
    if (side == FIXED) {
        // Fixed side deposits
        // no refunds allowed
        require(amount <= fixedSideCapacity - fixedETHDepositToken.totalSupply(), "OED");
        // Stake on Lido
        uint256 shares = lidoAdapter.stakeFunds{value: amount}(msg.sender);
        // Mint claim tokens
        fixedClaimToken.mint(msg.sender, shares);
        fixedETHDepositToken.mint(msg.sender, amount);
        emit FixedFundsDeposited(amount, shares, msg.sender);
    } else {
        // Variable side deposits
        // no refunds allowed
        require(amount <= variableSideCapacity - variableBearerToken.totalSupply(), "OED");
        // Mint bearer tokens
        variableBearerToken.mint(msg.sender, amount);
        emit VariableFundsDeposited(amount, msg.sender);
    }
}
```

## Recommendation
Deposit function should refund user in case if msg.value is greater than the current vault capacity.
