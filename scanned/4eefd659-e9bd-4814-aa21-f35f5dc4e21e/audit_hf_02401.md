# [H] Incorrect Claimable Fee Calculation in SafeStakeNetworkV3

## Summary
Severity: High
Contest weight: 0.6354
Dataset id: 12947
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, the SafeStake protocol distributes validator rewards to to its operators. In the process of analyzing the logic to compute claimable fee for related operators, we notice an issue that may use stale state for the fee calculation.
In the following, we show the implementation of the vulnerable accountClaimFee() routine. As the name indicates, this routine allows for claiming the operator fee for the given account. We notice the fee calculation is based on the following statement (line 227): can_claim = (endBlockNumber - detail.startBlockNumber)* detail.lastOperatorFee + op_detail.earnings, where the detail.startBlockNumber state should be replaced as max(detail.startBlockNumber, op_detail.lastBlockNumber). Note other two routines getOperatorEarningsByPublicKey() and _removeValidatorUnsafe() share the same issue.
```solidity
function accountClaimFee(address account, uint32[] calldata operatorIds, uint32[] calldata performances, uint256 nonce, bytes memory signature) external checkClaimNonce(nonce){
    bytes32 hash = prefixed(
        keccak256(
            abi.encode(account, operatorIds, performances, nonce)
        )
    );
    address signer = recoverSigner(hash, signature);
    require(hasRole(SIGNER_ROLE, signer),"G1");
    uint256 claimed = 0;
    uint256 penalty = 0;
    for(uint32 a=0; a < operatorIds.length; ++a) {
        uint32 operatorId = operatorIds[a];
        require(performances[a] <= 100,"G2");
        uint256 earnings = 0;
        for(uint32 b=0; b < _operatorInDatas[operatorId].length; ++b) {
            bytes memory publicKey = _operatorInDatas[operatorId][b].publicKey;
            ValidatorData storage detail = _validatorDatas[publicKey];
            OperatorWorkDetail storage op_detail = _operatorWorkDetail[operatorId][publicKey];
            uint256 endBlockNumber = detail.endBlockNumber <= block.number ? detail.endBlockNumber : block.number;
            uint256 can_claim = (endBlockNumber - detail.startBlockNumber) * detail.lastOperatorFee + op_detail.earnings;
            op_detail.earnings = 0;
            op_detail.lastBlockNumber = block.number;
            earnings += can_claim;
            uint256 true_claim = earnings * performances[a] / 100;
            penalty += earnings - true_claim;
            claimed += true_claim;
            self.networkPenalty += penalty;
            require(_token.transfer(account, claimed), "G3");
            _claimNonce[nonce] = true;
            emit AccountClaim(nonce, account, claimed, penalty, block.number);
        }
    }
}
```

## Recommendation
Revise the above routine to properly update operator fees.
