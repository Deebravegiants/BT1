### Title
One-Step `setContract()` Enables Irrecoverable Misdirection of Protocol Fee Yield to Wrong Treasury - (File: `contracts/LRTConfig.sol`)

---

### Summary
`LRTConfig.setContract()` updates any critical protocol contract address — including `PROTOCOL_TREASURY` — in a single transaction with no confirmation step. If the admin supplies an incorrect address for `PROTOCOL_TREASURY`, all protocol fees subsequently minted as rsETH by the publicly callable `LRTOracle.updateRSETHPrice()` are permanently sent to the wrong address before the admin can correct the mistake.

---

### Finding Description
`LRTConfig.setContract()` is a one-step setter with no pending/accept pattern:

```solidity
function setContract(bytes32 contractKey, address contractAddress)
    external onlyRole(DEFAULT_ADMIN_ROLE)
{
    _setContract(contractKey, contractAddress);
}

function _setContract(bytes32 key, address val) private {
    UtilLib.checkNonZeroAddress(val);          // only rejects address(0)
    if (contractMap[key] == val) revert ValueAlreadyInUse();
    contractMap[key] = val;
    emit SetContract(key, val);
}
``` [1](#0-0) 

The only guard is a non-zero check. Any non-zero wrong address is accepted and immediately live. Among the keys managed by this function is `PROTOCOL_TREASURY`: [2](#0-1) 

`PROTOCOL_TREASURY` is consumed inside `LRTOracle._updateRsETHPrice()`, which mints protocol fees directly to whatever address `getContract(PROTOCOL_TREASURY)` returns:

```solidity
address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
``` [3](#0-2) 

`updateRSETHPrice()` is a permissionless public function: [4](#0-3) 

Once a fee-minting call executes against the wrong treasury address, those rsETH tokens are minted and gone. The admin can subsequently correct `PROTOCOL_TREASURY` via another `setContract()` call, but the already-minted fees are irrecoverable.

---

### Impact Explanation
**High — Theft of unclaimed yield.**

Protocol fees accumulate as rsETH minted to `PROTOCOL_TREASURY`. A single mistaken `setContract()` call pointing `PROTOCOL_TREASURY` at a wrong address causes every subsequent `updateRSETHPrice()` invocation (callable by anyone) to mint fee rsETH to that wrong address. The minted tokens cannot be recalled; the protocol permanently loses the yield that should have accrued to its treasury.

---

### Likelihood Explanation
**Low-to-Medium.**

The admin is a privileged role, but human error (copy-paste mistake, wrong address in a script, transaction reuse) is a realistic operational risk — exactly the scenario the two-step pattern is designed to prevent. `updateRSETHPrice()` is public and is expected to be called frequently (every price update cycle), so the window between a mistaken `setContract()` and the first fee-minting call is short.

---

### Recommendation
Adopt a two-step commit/accept pattern for `setContract()` (and similarly for `setRSETH()`, `setToken()`, and `setEigenLayerRewardReceiver()`):

1. **Propose**: admin calls `proposeContract(key, newAddress)`, storing a `pendingContractMap[key]` and emitting an event.
2. **Accept** (after a time-lock or explicit confirmation): admin calls `acceptContract(key)`, which moves `pendingContractMap[key]` into `contractMap[key]`.

This ensures a wrong address can be cancelled before it takes effect, and gives monitoring systems time to detect and alert on unexpected changes.

---

### Proof of Concept

1. Admin intends to update `PROTOCOL_TREASURY` to `0xCorrect` but accidentally submits `0xWrong` (e.g., a copy-paste error):
   ```
   LRTConfig.setContract(PROTOCOL_TREASURY, 0xWrong)
   ``` [5](#0-4) 

2. `_setContract` accepts `0xWrong` because it is non-zero and differs from the current value. `contractMap[PROTOCOL_TREASURY]` is now `0xWrong`. [6](#0-5) 

3. Any external caller (depositor, keeper, MEV bot) calls the public `updateRSETHPrice()`: [4](#0-3) 

4. Inside `_updateRsETHPrice()`, protocol fees are minted to `0xWrong`:
   ```solidity
   address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY); // returns 0xWrong
   IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
   ``` [3](#0-2) 

5. Admin notices the error and calls `setContract(PROTOCOL_TREASURY, 0xCorrect)`. Future fees go to the right address, but all rsETH already minted to `0xWrong` is permanently lost — there is no recovery mechanism.

### Citations

**File:** contracts/LRTConfig.sol (L237-251)
```text
    function setContract(bytes32 contractKey, address contractAddress) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _setContract(contractKey, contractAddress);
    }

    /// @dev private function to set a contract
    /// @param key Contract key
    /// @param val Contract address
    function _setContract(bytes32 key, address val) private {
        UtilLib.checkNonZeroAddress(val);
        if (contractMap[key] == val) {
            revert ValueAlreadyInUse();
        }
        contractMap[key] = val;
        emit SetContract(key, val);
    }
```

**File:** contracts/utils/LRTConstants.sol (L21-21)
```text
    bytes32 public constant PROTOCOL_TREASURY = keccak256("PROTOCOL_TREASURY");
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L304-307)
```text
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
```
