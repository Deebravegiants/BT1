# [H] Force Investment Risk in Bank

## Summary
Severity: High
Contest weight: 0.6363
Dataset id: 12842
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Rabbit protocol is a leveraged trading protocol based on deposit and borrowing functions. It is inspired from the Alpha/Alpaca framework and thus shares similar architecture with vault, worker, and strategies. While examining the vault implementation (inside the Bank contract), we notice a potential force investment risk that has been exploited in earlier hacks, e.g., yDAI [15] and BT.Finance [1]. To elaborate, we show below the related Bank::work() routine. Specificaly, the Bank contract is designed and implemented to invest borrowed funds (held in Bank), harvest growing yields, and return any gains, if any, to the users. For safety, the protocol requires each position is subject to the health check (lines 1001-1002) for each borrow-related operation.
```solidity
function work(uint256 posId, uint256 pid, uint256 borrow, bytes calldata data) external payable onlyEOA nonReentrant {
    if (posId == 0) {
        posId = currentPos;
        currentPos++;
        positions[posId].owner = msg.sender;
        positions[posId].productionId = pid;
        positions[posId].debtShare = 0;
        userPosition[msg.sender].push(posId);
    } else {
        require(posId < currentPos, "bad position id");
        require(positions[posId].owner == msg.sender, "not position owner");
        pid = positions[posId].productionId;
    }
    Production storage production = productions[pid];
    require(production.isOpen, "Production not exists");
    require(borrow == 0 || production.canBorrow, "Production can not borrow");
    calInterest(production.borrowToken);
    uint256 debt = _removeDebt(posId, production).add(borrow);
    bool isBorrowBNB = production.borrowToken == address(0);
    uint256 sendBNB = msg.value;
    uint256 beforeToken = 0;
    if (isBorrowBNB) {
        sendBNB = sendBNB.add(borrow);
        require(sendBNB <= address(this).balance && debt <= banks[production.borrowToken].totalVal, "insufficient BNB in the bank");
        beforeToken = address(this).balance.sub(sendBNB);
    } else {
        beforeToken = SafeToken.myBalance(production.borrowToken);
        require(borrow <= beforeToken && debt <= banks[production.borrowToken].totalVal, "insufficient borrowToken in the bank");
        beforeToken = beforeToken.sub(borrow);
        SafeToken.safeApprove(production.borrowToken, production.goblin, borrow);
    }
    Goblin(production.goblin).work{value: sendBNB}(posId, msg.sender, production.borrowToken, borrow, debt, data);
    uint256 backToken = isBorrowBNB ? (address(this).balance.sub(beforeToken)) : SafeToken.myBalance(production.borrowToken).sub(beforeToken);
    if (backToken > debt) {
        backToken = backToken.sub(debt);
        debt = 0;
        isBorrowBNB ? SafeToken.safeTransferETH(msg.sender, backToken) : SafeToken.safeTransfer(production.borrowToken, msg.sender, backToken);
    } else if (debt > backToken) {
        debt = debt.sub(backToken);
        backToken = 0;
        require(debt >= production.minDebt && debt <= production.maxDebt, "Debt scale is out of scope");
        uint256 health = Goblin(production.goblin).health(posId, production.borrowToken);
        require(health.mul(production.openFactor) >= debt.mul(GLO_VAL), "bad work factor");
        _addDebt(posId, production, debt);
    }
    emit Work(posId, debt, backToken);
```
It comes to our attention that the health check does not have the stability check on the liquidity pool into which the borrowed funds will be added. In other words, if the configured strategy blindly invests the deposited funds into an imbalanced Ellipse/PancakeSwap pool, the strategy will not result in a profitable investment. In fact, earlier incidents (yDAI and BT.Finance hacks [1, 15]) have prompted the need of a guarded call before kicking off the actual investment. For the very same reason, we argue for the guarded stability check associated with every single health() call.

## Recommendation
Ensure the target liquidity pool is stable before the borrowed funds can be added into as liquidity.
