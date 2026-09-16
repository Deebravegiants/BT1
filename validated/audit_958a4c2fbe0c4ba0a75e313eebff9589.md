### Title
Unrestricted `superApprove()` lets any caller grant unlimited token allowances on behalf of any `HyperFungibleTokenImpl` holder - ([File: evm/src/utils/HyperFungibleTokenImpl.sol])

### Summary
`HyperFungibleTokenImpl` is the production cross-chain fungible token implementation used for Hyperbridge's token bridging (deployed via `evm/script/DeployIsmp.s.sol`, used by the fee token and faucet flows). It exposes a `public` function `superApprove(address owner, address spender)` with **no access control and no signature/authorization from `owner`**, which directly calls the internal `_approve(owner, spender, type(uint256).max)`. [1](#0-0) 

Any unprivileged address can call `token.superApprove(victim, attacker)` to grant `attacker` an unlimited (`type(uint256).max`) allowance over `victim`'s token balance — no `msg.sender == owner` check exists at all. This is a direct, and in fact more severe, analog of the reported `OmoRouter.approve()` bug class: an unprivileged party can create/self-assign unauthorized ERC-20 approvals, except here the victim is an arbitrary third-party token holder rather than the router itself.

### Finding Description
The function is documented as a "Helper function for tests" but lives in `evm/src/utils/` (production `src` tree, not a `tests/` directory) and is `public`, with no `onlyRole`, `onlyOwner`, or `msg.sender == owner` guard: [2](#0-1) [1](#0-0) 

Every other privileged action in the same contract (`mint`, `burn`, `grantMinterRole`, `grantBurnerRole`, `revokeMinterRole`, `revokeBurnerRole`) is correctly gated with `onlyRole(...)`: [3](#0-2) 

`superApprove` is the sole exception, contradicting the access-control pattern of the rest of the contract. Since `_approve` is OpenZeppelin's internal ERC-20 primitive that unconditionally sets the allowance mapping regardless of caller identity, exposing it publicly without an owner-authenticity check means **any address can set an allowance on any other holder's balance for any spender** — including themselves.

This contract is referenced from the deployment script (`evm/script/DeployIsmp.s.sol`) and from `TokenFaucet.sol`, which mints faucet tokens to users of `HyperFungibleTokenImpl`: [4](#0-3) 

This indicates the token is deployed and used in live/testnet fee-token and faucet contexts, not confined to Foundry test mocks (unlike the near-identical `superApprove` helpers found in `evm/tests/foundry/MockUSDC.sol`, which are legitimately test-only mocks).

### Impact Explanation
An attacker can drain any balance held by users of this token by:
1. Calling `superApprove(victim, attacker)` to grant themselves `type(uint256).max` allowance over the victim's tokens.
2. Calling `transferFrom(victim, attacker, victim.balanceOf(victim))` to steal the full balance.

Given this token is intended as a fee/bridged token within the Hyperbridge ecosystem (fee payments for message dispatch, bandwidth, faucet drips), this constitutes concrete theft of funds for any holder, satisfying the "concrete theft ... of funds" validation bar.

### Likelihood Explanation
Likelihood is high: the function is `public`, requires no special permissions, no proof, no signature, and can be called by literally any EOA or contract in a single transaction against any deployed instance of `HyperFungibleTokenImpl`. The only barrier is convincing/awaiting a victim to hold a balance of the token, which is trivially true for anyone who has used the faucet or holds the fee token.

### Recommendation
Remove `superApprove()` from the production `HyperFungibleTokenImpl` contract entirely, or, if a test helper is genuinely required, move it exclusively into the Foundry test/mock sources (as already done correctly in `evm/tests/foundry/MockUSDC.sol`) and never ship it in the deployable production implementation. If some approve-helper functionality is required for tooling, gate it with `require(msg.sender == owner)` or an explicit signed permit, matching ERC-2612 semantics.

### Proof of Concept
```solidity
// Attacker contract/EOA — no special role needed
HyperFungibleTokenImpl token = HyperFungibleTokenImpl(TOKEN_ADDRESS);

// victim holds a balance, e.g. from TokenFaucet.drip() or fee-token distribution
address victim = 0xVictim;

// 1. Attacker grants themselves unlimited allowance over victim's tokens
token.superApprove(victim, address(this));

// 2. Attacker drains victim's full balance
uint256 bal = token.balanceOf(victim);
token.transferFrom(victim, address(this), bal);
``` [1](#0-0)

### Citations

**File:** evm/src/utils/HyperFungibleTokenImpl.sol (L26-42)
```text
contract HyperFungibleTokenImpl is ERC20, AccessControlEnumerable {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER ROLE");

    /// @notice Custom error thrown when a non-gateway address attempts to mint or burn
    error OnlyGateway();

    /**
     * @notice Initializes the token with a name, symbol, and admin
     * @param admin The address that will have DEFAULT_ADMIN_ROLE to grant/revoke roles
     * @param name The name of the token
     * @param symbol The symbol of the token
     */
    constructor(address admin, string memory name, string memory symbol) ERC20(name, symbol) {
        require(admin != address(0), "Admin cannot be zero address");
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }
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
