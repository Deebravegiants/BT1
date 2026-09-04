Confirmed: there is no ERC20 whitelist — any depositor can specify an arbitrary `erc20TokenAddresses[i]` in `CircomData`, including a fee-on-transfer/deflationary token, and only the standard `dimensionsCheck`/`checkOnchainCreation` structural checks are performed [1](#0-0) . This confirms the root cause of the deposit-path balance mismatch.

### Title
Deflationary/fee-on-transfer ERC20 deposits mint unbacked shielded balance in `_internalTransact` - (File: contracts/Hinkal.sol)

### Summary
The proof-gated deposit path in `Hinkal.transact` → `_internalTransact` trusts the prover-supplied `amountChanges[i]` as the exact amount credited to the shielded pool, but never verifies that the Hinkal contract's actual token balance increased by that amount. For fee-on-transfer/deflationary ERC20 tokens, the contract receives less than `amountChanges[i]`, while the shielded ledger (enforced by the circuit's `inTotal + amountChanges[i] === outTotal` constraint) is credited with the full declared amount, creating shielded value with no backing.

### Finding Description
When a user deposits (`deltaAmountChange > 0`), `_internalTransact` pulls tokens via `transferERC20TokenFromOrCheckETH` and immediately moves on without any before/after balance check: [2](#0-1) 

Compare this to the proofless-deposit path, `_handleTransfersFromProoflessDeposit`, which explicitly measures `balanceBefore`/`balanceAfter` and reverts unless `balanceAfter - balanceBefore == amount`: [3](#0-2) 

No such check exists for the proof-based `transact` deposit flow. The `amountChanges[i]` value used for the transfer is the same value that is a public input to the circuit and constrains the shielded-note equality inside `MainEVMCircuit`: [4](#0-3) 

The circuit only knows the *declared* `amountChanges[i]`; it has no way to know the *actual* number of tokens the contract received. Since `erc20TokenAddresses[i]` is fully attacker-controlled and unrestricted — there is no token whitelist anywhere in `HinkalHelper.performHinkalChecks`/`dimensionsCheck`/`checkOnchainCreation` — an attacker can deposit using a token that takes a transfer fee (or is otherwise deflationary), declare `amountChanges[i]` equal to the pre-fee amount, and receive `outCommitments` (new shielded UTXOs) that fully credit the pre-fee amount even though the contract only received the post-fee amount. This breaks the balance equality between the pool's real ERC20 balance and the sum of shielded value the circuit believes is backed, i.e., value is credited to the shielded ledger without a corresponding on-chain balance increase.

### Impact Explanation
This is unbacked minting of shielded value: the attacker's new UTXO(s) represent more token balance than was actually transferred into the pool. When the attacker (or a colluding recipient) later withdraws via a normal `transact` withdrawal for that token, the withdrawal is paid out of the shared token balance of the Hinkal contract — meaning the shortfall is ultimately paid for out of other depositors' funds for that same token, since the accounting ledger (nullifiers/commitments) no longer matches the real balance. This is a direct insolvency/theft vector against the shared token pool and matches the "Critical: minting shielded value without backing" category.

### Likelihood Explanation
Any unprivileged EOA can trigger this: no relayer, admin, or privileged role is required, and any ERC20 address can be supplied in `erc20TokenAddresses` since there is no whitelist. The only precondition is that a deflationary/fee-on-transfer or otherwise non-standard-transfer token exists in the token registry the front end/off-chain circuit builder allows — which is exactly the class of tokens flagged in the original report. The attacker fully controls the `CircomData.amountChanges`, `erc20TokenAddresses`, and can generate a valid ZK proof for arbitrary self-chosen output amounts (subject to the circuit's own arithmetic identity, which does not reference actual balances).

### Recommendation
Add the same balance-before/after invariant used in `_handleTransfersFromProoflessDeposit` to the deposit branch of `_internalTransact`: after calling `transferERC20TokenFromOrCheckETH` for a positive `deltaAmountChange`, measure `getERC20OrETHBalance` before and after and require the delta equals `circomData.amountChanges[i]` (or, alternatively, adopt an explicit allow-list of tokens known to be standard-conforming, non-fee-on-transfer, non-rebasing).

### Proof of Concept
1. Deploy/select a fee-on-transfer ERC20 token `T` that deducts, e.g., a 5% fee on `transferFrom` (this class of tokens exists on mainnet, e.g. certain reflection/tax tokens).
2. Attacker builds a valid ZK proof off-chain for `transact()` with `erc20TokenAddresses = [T]`, `amountChanges = [100]`, `inputNullifiers = []` (no inputs spent), and `outCommitments` representing a new 100-token UTXO for token `T`. The circuit only checks `inTotal(0) + amountChanges(100) === outTotal(100)` — an arithmetic identity satisfied regardless of real transfer amounts, see [4](#0-3) .
3. Call `Hinkal.transact(...)`. `_internalTransact` executes `transferERC20TokenFromOrCheckETH(T, attacker, address(this), 100)`, which internally calls `safeTransferFrom` for 100 tokens, see [5](#0-4) . Due to the 5% fee, the Hinkal contract's actual `T` balance only increases by 95.
4. No check compares 95 (actual) to 100 (declared); the transaction succeeds and a new shielded UTXO worth 100 `T` is inserted into the tree.
5. The attacker (or anyone with the corresponding spending key) can later withdraw the full 100 `T` via a normal `transact()` withdrawal, which pulls from the shared contract balance backed by other users' deposits, effectively minting 5 tokens of unbacked value at the expense of the shared pool.

### Citations

**File:** contracts/HinkalHelper.sol (L64-90)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
        require(
            circomData.amountChanges.length == dimensions.tokenNumber,
            "AmountChanges number should be equal to token number"
        );

        require(
            circomData.onChainCreation.length == dimensions.tokenNumber,
            "onchain creation is equal to tokens count"
        );

        require(
            circomData.slippageValues.length == dimensions.tokenNumber,
            "slippageValues length should be equal to tokens count"
        );

        require(
            circomData.inputNullifiers.length == dimensions.tokenNumber,
            "InputNullifiers number should be equal to token number"
        );
```

**File:** contracts/Hinkal.sol (L172-188)
```text
    function _internalTransact(CircomData calldata circomData) private {
        bool hasPaidToRelay = false;
        for (uint64 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 deltaAmountChange = _calculateDeltaAmount(circomData, i);

            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
            } else {
```

**File:** contracts/Hinkal.sol (L356-381)
```text
    function _handleTransfersFromProoflessDeposit(
        TokenWithAmount[] memory uniqueTokens,
        uint256 uniqueCount
    ) private {
        for (uint256 i = 0; i < uniqueCount; i++) {
            address erc20Address = uniqueTokens[i].erc20Address;
            uint256 amount = uniqueTokens[i].amount;

            uint256 balanceBefore = getERC20OrETHBalance(erc20Address);
            if (erc20Address == address(0)) balanceBefore -= msg.value;

            transferERC20TokenFromOrCheckETH(
                erc20Address,
                msg.sender,
                address(this),
                amount
            );

            uint256 balanceAfter = getERC20OrETHBalance(erc20Address);

            require(
                balanceAfter - balanceBefore == amount,
                "proofless deposit balances must be equal"
            );
        }
    }
```

**File:** circuits/MainEVMCircuit.circom (L166-169)
```text

      // for each token type, the sum of refund and swapped amount should be equal to the sum of input amounts
      inTotal + amountChanges[i] === outTotal;
	}
```
