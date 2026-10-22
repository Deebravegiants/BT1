# [H] Anyone can call VVVVCTokenDist

## Summary
Severity: High
Contest weight: 0.9034
Dataset id: 1830
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
pepocpeter, plairfx, prgzro, redbeans, rsam_eth, shaflow01, udo, vladi319, whitehair0330, wildflowerzx, y4y  
Legitimate users can claim their reward with the ClaimParams signed by the signer. However, the VVVVCTokenDistribution::claim function just checks the validity of the signed params and doesn't check the caller is the right claimer. Hence anyone can claim the legitimate users' rewards by front-running the signed ClaimParams and because of the nonce increase legitimate users can't claim their reward.  
aaa66de349ef1b9e4bd331f14b/vvv-platform-smart-contracts/contracts/vc/VVVVCTokenDistributor.sol#L133  
Internal pre-conditions  
N/A  
External pre-conditions  
Legitimate users call claim function with signed params.  
Attack Path  
The VVVVCTokenDistribution::claim function is as follows:  
```solidity
function claim(ClaimParams memory _params) public {
    if (claimIsPaused) {
        revert ClaimIsPaused();
    }

    if (_params.projectTokenProxyWallets.length != _params.tokenAmountsToClaim.length) {
        revert ArrayLengthMismatch();
    }

    if (_params.nonce <= nonces[_params.kycAddress]) {
        revert InvalidNonce();
    }

    if (!_isSignatureValid(_params)) {
        revert InvalidSignature();
    }

    // update nonce
    nonces[_params.kycAddress] = _params.nonce;

    // define token to transfer
    IERC20 projectToken = IERC20(_params.projectTokenAddress);

    // transfer tokens from each wallet to the caller
    for (uint256 i = 0; i < _params.projectTokenProxyWallets.length; i++) {
        projectToken.safeTransferFrom(
            _params.projectTokenProxyWallets[i],
            msg.sender,
            _params.tokenAmountsToClaim[i]
        );
    }

    emit VCClaim(
        _params.kycAddress,
        _params.projectTokenAddress,
        _params.projectTokenProxyWallets,
        _params.tokenAmountsToClaim,
        _params.nonce
    );
}
```
At L119, the function checks the validity of the input params.  
The _isSignatureValid function is as follows:  
```solidity
function _isSignatureValid(ClaimParams memory _params) private view returns (bool) {
    bytes32 digest = keccak256(
        abi.encodePacked(
            "\x19\x01",
            DOMAIN_SEPARATOR,
            keccak256(
                abi.encode(
                    CLAIM_TYPEHASH,
                    _params.kycAddress,
                    _params.projectTokenAddress,
                    _params.projectTokenProxyWallets,
                    _params.tokenAmountsToClaim,
                    _params.nonce,
                    _params.deadline
                )
            )
        )
    );

    address recoveredAddress = ECDSA.recover(digest, _params.signature);

    bool isSigner = recoveredAddress == signer;
    bool isExpired = block.timestamp > _params.deadline;
    return isSigner && !isExpired;
}
```
The function just checks if the signature is signed by the signer. The VVVVCTokenDistribution::claim function doesn't check if the msg.sender is the kycAddress and this leads to anyone can claim legitimate kycAddress reward by front-running the params. Besides at L124, it increases the nonce of the kycAddress to prevent the double claim, hence the legitimate claimer can't claim their rewards.  
Though, front-running may be hard on L2 but this leads to loss of fund to users and it will be deployed on Ethereum also.  
Anyone can claim other legitimate users' rewards and the legitimate users can't claim their rewards.

## Recommendation
It is recommended to send the reward to the kycAddress not the msg.sender.  
```solidity
function claim(ClaimParams memory _params) public {
    if (claimIsPaused) {
        revert ClaimIsPaused();
    }
    if (_params.projectTokenProxyWallets.length != _params.tokenAmountsToClaim.length) {
        revert ArrayLengthMismatch();
    }
    if (_params.nonce <= nonces[_params.kycAddress]) {
        revert InvalidNonce();
    }
    if (!_isSignatureValid(_params)) {
        revert InvalidSignature();
    }
    // update nonce
    nonces[_params.kycAddress] = _params.nonce;
    // define token to transfer
    IERC20 projectToken = IERC20(_params.projectTokenAddress);
    // transfer tokens from each wallet to the caller
    for (uint256 i = 0; i < _params.projectTokenProxyWallets.length; i++) {
        projectToken.safeTransferFrom(
            _params.projectTokenProxyWallets[i],
            _params.kycAddress,
            _params.tokenAmountsToClaim[i]
        );
    }
    emit VCClaim(
        _params.kycAddress,
        _params.projectTokenAddress,
        _params.projectTokenProxyWallets,
        _params.tokenAmountsToClaim,
        _params.nonce
    );
}
```
