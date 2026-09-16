### Title
Unrestricted `superApprove()` allows anyone to drain any holder's `HyperFungibleTokenImpl` balance - (File: evm/src/utils/HyperFungibleTokenImpl.sol)

### Summary
`HyperFungibleTokenImpl.sol` contains a `superApprove(address owner, address spender)` function that sets an unlimited ERC20 allowance from an arbitrary `owner` to an arbitrary `spender`, callable by anyone with no access control. This is the analog of the reported Bancor `trade()` issue — leftover, unused-in-production code with no restriction — except here the unrestricted function is directly exploitable to steal token balances rather than being merely dead code.

### Finding Description
`HyperFungibleTokenImpl` is a role-gated cross-chain fungible token used by Hyperbridge's token-bridge tooling (deployed via `evm/script/DeployIsmp.s.sol` and consumed by `evm/src/utils/TokenFaucet.sol`, which calls its `mint()`). [1](#0-0) 

The contract properly gates `mint`/`burn`/role-management behind `onlyRole(...)`: [2](#0-1) 

But `superApprove` has no modifier at all:
```solidity
function superApprove(address owner, address spender) public {
    _approve(owner, spender, type(uint256).max);
}
``` [1](#0-0) 

Its own doc comment labels it a test helper ("Helper function for tests - approves unlimited tokens"), confirming it is leftover/dead-for-production code, matching the report's bug class of an unused, unrestricted function accidentally left in the contract. Unlike the Bancor `trade()` report (which the source noted has no known attack vector), this function is directly weaponizable: any attacker can call `superApprove(victim, attacker)` on any deployed `HyperFungibleTokenImpl` instance to set `allowance[victim][attacker] = type(uint256).max`, then call the standard ERC20 `transferFrom(victim, attacker, balanceOf(victim))` to drain the victim's entire token balance.

### Impact Explanation
Any holder of a token minted via this implementation (e.g., faucet-distributed test/bridge tokens through `TokenFaucet.drip`) can have their entire balance stolen by an arbitrary caller, with no privilege required. This is a direct, unrestricted theft-of-funds vector on any token deployed from this contract. [3](#0-2) 

### Likelihood Explanation
High: `superApprove` is `public`, takes attacker-controlled `owner`/`spender` parameters, has zero access-control modifiers, and is reachable in a single transaction by any external account against any deployed instance of the token. [4](#0-3) 

### Recommendation
Remove `superApprove` entirely from `HyperFungibleTokenImpl.sol` (move any test-only approval helper into the test suite instead), consistent with the reported recommendation to strip unused, unrestricted code from production contracts.

### Proof of Concept
```solidity
// Assume `token` is a deployed HyperFungibleTokenImpl with `victim` holding a balance
// (e.g. via TokenFaucet.drip minting to victim).

// Attacker, with no role/permission, calls:
token.superApprove(victim, address(attackerContract));

// allowance[victim][attackerContract] is now type(uint256).max

// Attacker drains victim's balance via standard ERC20:
uint256 stolen = token.balanceOf(victim);
token.transferFrom(victim, address(attackerContract), stolen);
``` [5](#0-4)

### Citations

**File:** evm/src/utils/HyperFungibleTokenImpl.sol (L26-31)
```text
contract HyperFungibleTokenImpl is ERC20, AccessControlEnumerable {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER ROLE");

    /// @notice Custom error thrown when a non-gateway address attempts to mint or burn
    error OnlyGateway();
```

**File:** evm/src/utils/HyperFungibleTokenImpl.sol (L64-76)
```text
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        _mint(to, amount);
    }

    /**
     * @notice Burns tokens from the specified account
     * @dev Can be called by any address with BURNER_ROLE
     * @param from The address from which tokens will be burned
     * @param amount The amount of tokens to burn
     */
    function burn(address from, uint256 amount) external onlyRole(BURNER_ROLE) {
        _burn(from, amount);
    }
```

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
