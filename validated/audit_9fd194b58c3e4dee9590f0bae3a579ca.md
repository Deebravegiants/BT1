This is deployed as the **fee token** in production Hyperbridge deployments (via `DeployIsmp.s.sol`) and integrates with `TokenFaucet` for drips. The `superApprove` function is public, unrestricted, and grants unlimited ERC-20 allowance to any spender for any token holder's balance — directly analogous to the reported `approveToRouter` bug.

### Title
Unrestricted `superApprove` in `HyperFungibleTokenImpl` grants unlimited allowance for any owner to any spender - (File: `evm/src/utils/HyperFungibleTokenImpl.sol`)

### Summary
`HyperFungibleTokenImpl.superApprove(address owner, address spender)` is a `public` function with no access control that calls `_approve(owner, spender, type(uint256).max)`, letting any caller grant unlimited ERC-20 spending allowance from an arbitrary `owner` to an arbitrary `spender`, without the `owner`'s consent.

### Finding Description
`HyperFungibleTokenImpl` is an `ERC20`/`AccessControlEnumerable` token that gates `mint`/`burn` behind `MINTER_ROLE`/`BURNER_ROLE`, but its `superApprove` function bypasses all access control: [1](#0-0) 
Unlike OpenZeppelin's `_approve`, which normally requires `msg.sender == owner` (enforced at the public `approve(spender, amount)` wrapper), this function exposes the internal `_approve` primitive directly to any caller, letting them designate *any* address as `owner` and *any* address as `spender`, with `type(uint256).max` allowance. This is architecturally identical to the reported `approveToRouter` bug in USSD.sol, where a public function with a hardcoded max-uint approval bypassed access control — except here the caller also controls the `owner` and `spender` parameters, making it strictly worse: it does not merely approve a fixed spender, it can set unlimited allowance from *any token holder* to *any spender the attacker chooses* (e.g. the attacker's own address).

This contract is used as the network's fee token in production deployments, wired up in `DeployIsmp.s.sol`: [2](#0-1) 
and consumed by `TokenFaucet.drip`, which mints tokens to callers of this exact token type: [3](#0-2) 

### Impact Explanation
Any unprivileged address can call `superApprove(victim, attacker)` on the deployed `HyperFungibleTokenImpl` fee-token contract, granting the attacker's address unlimited allowance over the victim's fee-token balance. The attacker can then call `transferFrom(victim, attacker, balance)` to drain any holder's balance of this token — this is the network fee token used throughout the ISMP/Hyperbridge dispatch flow for paying dispatch/relayer fees (`dispatchWithFeeToken`, `IntentGatewayV2` fee handling, etc.), so draining balances directly enables theft of funds held by users, solvers, or protocol contracts that hold this token.

### Likelihood Explanation
Trivial and permissionless: the function is `public`, requires no role, no prior approval, and no special transaction context — a single call from any account is sufficient to compromise any token holder's balance in this contract instance.

### Recommendation
Remove `superApprove` from production code, or restrict it to a test-only mock contract that is never deployed as the live fee token / HyperFungibleTokenImpl instance. If a similar helper is needed for tests, gate it behind `onlyRole(DEFAULT_ADMIN_ROLE)` or move it into a separate mock contract not reachable in the deployed bytecode.

### Proof of Concept
1. Network deploys `HyperFungibleTokenImpl` as the fee token per `DeployIsmp.s.sol`.
2. A victim (`V`) holds a balance of the fee token (e.g. received via `TokenFaucet.drip` or by paying dispatch fees).
3. Attacker (`A`) calls `HyperFungibleTokenImpl(feeToken).superApprove(V, A)`.
4. Contract executes `_approve(V, A, type(uint256).max)` — no check that `msg.sender == V`.
5. Attacker calls `feeToken.transferFrom(V, A, feeToken.balanceOf(V))`, draining `V`'s entire balance. [1](#0-0)

### Citations

**File:** evm/src/utils/HyperFungibleTokenImpl.sol (L110-117)
```text
    /**
     * @notice Helper function for tests - approves unlimited tokens
     * @param owner The owner of the tokens
     * @param spender The spender address
     */
    function superApprove(address owner, address spender) public {
        _approve(owner, spender, type(uint256).max);
    }
```

**File:** evm/script/DeployIsmp.s.sol (L36-50)
```text
contract DeployScript is BaseScript {
    using strings for *;

    uint256 private paraId = vm.envUint("PARA_ID");

    /// @notice Main deployment logic - called by BaseScript's run() functions
    /// @dev This function is called within a broadcast context
    function deploy() internal override {
        uint256 decimals;
        address uniswapV2;
        address consensusClient;
        address feeToken;
        bytes memory hyperbridge;
        TokenFaucet faucet;
        HyperFungibleTokenImpl feeTokenInstance;
```

**File:** evm/src/utils/TokenFaucet.sol (L25-39)
```text
contract TokenFaucet {
    mapping(address => uint256) private consumers;

    // @dev Will only drip tokens, once per day
    function drip(address token) public {
        uint256 lastDrip = consumers[msg.sender];
        uint256 delay = block.timestamp - lastDrip;

        if (delay < 1 days) {
            revert("Can only request tokens once daily");
        }

        consumers[msg.sender] = block.timestamp;
        HyperFungibleTokenImpl(token).mint(msg.sender, 1000 * 1e18);
    }
```
