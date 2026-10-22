# [M] Fork-Resistant Domain Separator in AToken

## Summary
Severity: Medium
Contest weight: 0.5928
Dataset id: 12112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The various tokens in Geist are designed to strictly follows the widely-accepted ERC20 speciﬁcation (Section 3.4). In the meantime, we notice the support of EIP-2612 with the permit() function that allows for approvals to be made via secp256k1 signatures. Interestingly, we notice the state variable DOMAIN_SEPARATOR in AToken is initialized once inside the initialize() function (lines 81-89).

```solidity
function initialize(
    ILendingPool pool,
    address treasury,
    address underlyingAsset,
    IAaveIncentivesController incentivesController,
    uint8 aTokenDecimals,
    string calldata aTokenName,
    string calldata aTokenSymbol,
    bytes calldata params
) external override initializer {
    uint256 chainId;
    // solium-disable-next-line
    assembly {
        chainId := chainid()
    }
    DOMAIN_SEPARATOR = keccak256(
        abi.encode(
            EIP712_DOMAIN,
            keccak256(bytes(aTokenName)),
            keccak256(EIP712_REVISION),
            chainId,
            address(this)
        )
    );
    _setName(aTokenName);
    _setSymbol(aTokenSymbol);
    _setDecimals(aTokenDecimals);
    _pool = pool;
    _treasury = treasury;
    _underlyingAsset = underlyingAsset;
    _incentivesController = incentivesController;
    emit Initialized(
        underlyingAsset,
        address(pool),
        treasury,
        address(incentivesController),
        aTokenDecimals,
        aTokenName,
        aTokenSymbol,
        params
    );
}
```

The DOMAIN_SEPARATOR is used in the permit() function and should be unique to the contract and chain in order to prevent replay attacks from other domains. However, when analyzing this permit() routine, we realize the current implementation needs to be improved by recalculating the value of DOMAIN_SEPARATOR inside the permit() function, for the very purpose of preventing cross-chain replay attacks. Speciﬁcally, when there is a chain-level hard-fork, because of the pre-computed DOMAIN_SEPARATOR, a valid signature for one chain could be replayed on the other.

```solidity
function permit(
    address owner,
    address spender,
    uint256 value,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
) external {
    require(owner != address(0), "INVALID_OWNER");
    // solium-disable-next-line
    require(block.timestamp <= deadline, "INVALID_EXPIRATION");
    uint256 currentValidNonce = _nonces[owner];
    bytes32 digest = keccak256(
        abi.encodePacked(
            "\x19\x01",
            DOMAIN_SEPARATOR,
            keccak256(abi.encode(PERMIT_TYPEHASH, owner, spender, value, currentValidNonce, deadline))
        )
    );
    require(owner == ecrecover(digest, v, r, s), "INVALID_SIGNATURE");
    _nonces[owner] = currentValidNonce.add(1);
    _approve(owner, spender, value);
}
```

## Recommendation
Recalculate the value of DOMAIN_SEPARATOR inside the permit() function.
