# [?] Use PendleERC20 & add reentrancy protection

## Summary
Severity: Unknown
Chain: Pendle
Component: pendle-finance/pendle-core-v2-public
Published: 2022-06-08
Source: https://github.com/pendle-finance/pendle-core-v2-public/commit/1748cecdea3d1780d32195f30f144056fda7a005
Type: security-commit

## Details
Use PendleERC20 & add reentrancy protection

## Patch
### contracts/SuperComposableYield/base-implementations/SCYBase.sol
```diff
@@ -7,8 +7,9 @@ import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
 import "../../libraries/math/Math.sol";
 import "../../libraries/SCYUtils.sol";
 import "../../libraries/TokenHelper.sol";
+import "../../../contracts/core/PendleERC20.sol";
 
-abstract contract SCYBase is ISuperComposableYield, ERC20, ReentrancyGuard, TokenHelper {
+abstract contract SCYBase is ISuperComposableYield, PendleERC20, TokenHelper {
     using Math for uint256;
 
     address public immutable yieldToken;
@@ -24,7 +25,7 @@ abstract contract SCYBase is ISuperComposableYield, ERC20, ReentrancyGuard, Toke
         string memory _name,
         string memory _symbol,
         address _yieldToken
-    ) ERC20(_name, _symbol) {
+    ) PendleERC20(_name, _symbol, 18) {
         yieldToken = _yieldToken;
     }
 
@@ -69,7 +70,10 @@ abstract contract SCYBase is ISuperComposableYield, ERC20, ReentrancyGuard, Toke
     ) external nonReentrant updateReserve returns (uint256 amountTokenOut) {
         require(isValidBaseToken(tokenOut), "SCY: invalid tokenOut");
 
-        if (amountSharesToPull != 0) transferFrom(msg.sender, address(this), amountSharesToPull);
+        if (amountSharesToPull != 0) {
+            _spendAllowance(msg.sender, address(this), amountSharesToPull);
+            _transfer(msg.sender, address(this), amountSharesToPull);
+        }
 
         uint256 amountSharesToRedeem = _getFloatingAmount(address(this));
 
@@ -173,13 +177,6 @@ abstract contract SCYBase is ISuperComposableYield, ERC20, ReentrancyGuard, Toke
                 MISC METADATA FUNCTIONS
     //////////////////////////////////////////////////////////////*/
 
-    /**
-     * @notice See {ISuperComposableYield-decimals}
-     */
-    function decimals() public view virtual override(ERC20, IERC20Metadata) returns (uint8) {
-        return 18;
-    }
-
     /**
      * @notice See {ISuperComposableYield-getBaseTokens}
      */
```

### contracts/core/PendleBaseToken.sol
```diff
@@ -1,35 +0,0 @@
-// SPDX-License-Identifier: GPL-3.0-or-later
-pragma solidity 0.8.13;
-
-import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
-import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
-import "../interfaces/IPBaseToken.sol";
-
-abstract contract PendleBaseToken is ERC20, IPBaseToken {
-    uint8 private immutable _decimals;
-
-    uint256 public immutable timeCreated;
-    uint256 public immutable expiry;
-    address public immutable factory;
-
-    constructor(
-        string memory _name,
-        string memory _symbol,
-        uint8 __decimals,
-        uint256 _expiry
-    ) ERC20(_name, _symbol) {
-        require(_expiry > block.timestamp, "INVALID_EXPIRY");
-        _decimals = __decimals;
-        timeCreated = block.timestamp;
-        expiry = _expiry;
-        factory = msg.sender;
-    }
-
-    function decimals() public view virtual override(ERC20, IERC20Metadata) returns (uint8) {
-        return _decimals;
-    }
-
-    function isExpired() public view virtual returns (bool) {
-        return block.timestamp >= expiry;
-    }
-}
```

### contracts/core/PendleERC20.sol
```diff
@@ -0,0 +1,358 @@
+// SPDX-License-Identifier: MIT
+// OpenZeppelin Contracts (last updated v4.6.0) (token/ERC20/ERC20.sol)
+
+pragma solidity ^0.8.0;
+
+import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
+import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
+import "@openzeppelin/contracts/utils/Context.sol";
+
+/**
+ * @dev Pendle's ERC20 implementation, modified from @openzeppelin implementation
+ * Changes are:
+ * - comes with built-in reentrancy protection, storage-packed with totalSupply variable
+ * - delete increaseAllowance / decreaseAllowance
+ * - add nonReentrancy protection to transfer / transferFrom functions
+ * - allow decimals to by passed in
+ * - block self-transfer by default
+ *
+ */
+contract PendleERC20 is Context, IERC20, IERC20Metadata {
+    uint8 private constant _NOT_ENTERED = 1;
+    uint8 private constant _ENTERED = 2;
+
+    mapping(address => uint256) private _balances;
+
+    mapping(address => mapping(address => uint256)) private _allowances;
+
+    uint248 private _totalSupply;
+    uint8 private _status;
+
+    string private _name;
+    string private _symbol;
+    uint8 public immutable decimals;
+
+    /**
+     * @dev Prevents a contract from calling itself, directly or indirectly.
+     * Calling a `nonReentrant` function from another `nonReentrant`
+     * function is not supported. It is possible to prevent this from happening
+     * by making the `nonReentrant` function external, and making it call a
+     * `private` function that does the actual work.
+     */
+    modifier nonReentrant() {
+        // On the first call to nonReentrant, _notEntered will be true
+        require(_status != _ENTERED, "ReentrancyGuard: reentrant call");
+
+        // Any calls to nonReentrant after this point will fail
+        _status = _ENTERED;
+
+        _;
+
+        // By storing the original value once again, a refund is triggered (see
+        // https://eips.ethereum.org/EIPS/eip-2200)
+        _status = _NOT_ENTERED;
+    }
+
+    /**
+     * @dev Sets the values for {name} and {symbol}.
+     *
+     * The default value of {decimals} is 18. To select a different value for
+     * {decimals} you should overload it.
+     *
+     * All two of these values are immutable: they can only be set once during
+     * construction.
+     */
+    constructor(
+        string memory name_,
+        string memory symbol_,
+        uint8 _decimals
+    ) {
+        _name = name_;
+        _symbol = symbol_;
+        decimals = _decimals;
+        _status = _NOT_ENTERED;
+    }
+
+    /**
+     * @dev Returns the name of the token.
+     */
+    function name() public view virtual override returns (string memory) {
+        return _name;
+    }
+
+    /**
+     * @dev Returns the symbol of the token, usually a shorter version of the
+     * name.
+     */
+    function symbol() public view virtual override returns (string memory) {
+        return _symbol;
+    }
+
+    /**
+     * @dev See {IERC20-totalSupply}.
+     */
+    function totalSupply() public view virtual override returns (uint256) {
+        return _totalSupply;
+    }
+
+    /**
+     * @dev See {IERC20-balanceOf}.
+     */
+    function balanceOf(address account) public view virtual override returns (uint256) {
+        return _balances[account];
+    }
+
+    /**
+     * @dev See {IERC20-transfer}.
+     *
+     * Requirements:
+     *
+     * - `to` cannot be the zero address.
+     * - the caller must have a balance of at least `amount`.
+     */
+    function transfer(address to, uint256 amount)
+        external
+        virtual
+        override
+        nonReentrant
+        returns (bool)
+    {
+        address owner = _msgSender();
+        _transfer(owner, to, amount);
+        return true;
+    }
+
+    /**
+     * @dev See {IERC20-allowance}.
+     */
+    function allowance(address owner, address spender)
+        public
+        view
+        virtual
+        override
+        returns (uint256)
+    {
+        return _allowances[owner][spender];
+    }
+
+    /**
+     * @dev See {IERC20-approve}.
+     *
+     * NOTE: If `amount` is the maximum `uint256`, the allowance is not updated on
+     * `transferFrom`. This is semantically equivalent to an infinite approval.
+     *
+     * Requirements:
+     *
+     * - `spender` cannot be the zero address.
+     */
+    function approve(address spender, uint256 amount) external virtual override returns (bool) {
+        address owner = _msgSender();
+        _approve(owner, spender, amount);
+        return true;
+    }
+
+    /**
+     * @dev See {IERC20-transferFrom}.
+     *
+     * Emits an {Approval} event indicating the updated allowance. This is not
+     * required by the EIP. See the note at the beginning of {ERC20}.
+     *
+     * NOTE: Does not update the allowance if the current allowance
+     * is the maximum `uint256`.
+     *
+     * Requirements:
+     *
+     * - `from` and `to` cannot be the zero address.
+     * - `from` must have a balance of at least `amount`.
+     * - the caller must have allowance for ``from``'s tokens of at least
+     * `amount`.
+     */
+    function transferFrom(
+        address from,
+        address to,
+        uint256 amount
+    ) external virtual override nonReentrant returns (bool) {
+        address spender = _msgSender();
+        _spendAllowance(from, spender, amount);
+        _transfer(from, to, amount);
+        return true;
+    }
+
+    /**
+     * @dev Moves `amount` of tokens from `sender` to `recipient`.
+     *
+     * This internal function is equivalent to {transfer}, and can be used to
+     * e.g. implement automatic token fees, slashing mechanisms, etc.
+     *
+     * Emits a {Transfer} event.
+     *
+     * Requirements:
+     *
+     * - `from` cannot be the zero address.
+     * - `to` cannot be the zero address.
+     * - `from` must have a balance of at least `amount`.
+     */
+    function _transfer(
+        address from,
+        address to,
+        uint256 amount
+    ) internal virtual {
+        require(from != address(0), "ERC20: transfer from the zero address");
+        require(to != address(0), "ERC20: transfer to the zero address");
+        require(from != to, "ERC20: transfer to self");
+
+        _beforeTokenTransfer(from, to, amount);
+
+        uint256 fromBalance = _balances[from];
+        require(fromBalance >= amount, "ERC20: transfer amount exceeds balance");
+        unchecked {
+            _balances[from] = fromBalance - amount;
+        }
+        _balances[to] += amount;
+
+        emit Transfer(from, to, amount);
+
+        _afterTokenTransfer(from, to, amount);
+    }
+
+    /** @dev Creates `amount` tokens and assigns them to `account`, increasing
+     * the total supply.
+     *
+     * Emits a {Transfer} event with `from` set to the zero address.
+     *
+     * Requirements:
+     *
+     * - `account` cannot be the zero address.
+     */
+    function _mint(address account, uint256 amount) internal virtual {
+        require(account != address(0), "ERC20: mint to the zero address");
+
+        _beforeTokenTransfer(address(0), account, amount);
+
+        _totalSupply += toUint248(amount);
+        _balances[account] += amount;
+        emit Transfer(address(0), account, amount);
+
+        _afterTokenTransfer(address(0), account, amount);
+    }
+
+    /**
+     * @dev Destroys `amount` tokens from `account`, reducing the
+     * total supply.
+     *
+     * Emits a {Transfer} event with `to` set to the zero address.
+     *
+     * Requirements:
+     *
+     * - `account` cannot be the zero address.
+     * - `account` must have at least `amount` tokens.
+     */
+    function _burn(address account, uint256 amount) internal virtual {
+        require(account != address(0), "ERC20: burn from the zero address");
+
+        _beforeTokenTransfer(account, address(0), amount);
+
+        uint256 accountBalance = _balances[account];
+        require(accountBalance >= amount, "ERC20: burn amount exceeds balance");
+        unchecked {
+            _balances[account] = accountBalance - amount;
+        }
+        _totalSupply -= toUint248(amount);
+
+        emit Transfer(account, address(0), amount);
+
+        _afterTokenTransfer(account, address(0), amount);
+    }
+
+    /**
+     * @dev Sets `amount` as the allowance of `spender` over the `owner` s tokens.
+     *
+     * This internal function is equivalent to `approve`, and can be used to
+     * e.g. set automatic allowances for certain subsystems, etc.
+     *
+     * Emits an {Approval} event.
+     *
+     * Requirements:
+     *
+     * - `owner` cannot be the zero address.
+     * - `spender` cannot be the zero address.
+     */
+    function _approve(
+        address owner,
+        address spender,
+        uint256 amount
+    ) internal virtual {
+        require(owner != address(0), "ERC20: approve from the zero address");
+        require(spender != address(0), "ERC20: approve to the zero address");
+
+        _allowances[owner][spender] = amount;
+        emit Approval(owner, spender, amount);
+    }
+
+    /**
+     * @dev Updates `owner` s allowance for `spender` based on spent `amount`.
+     *
+     * Does not update the allowance amount in case of infinite allowance.
+     * Revert if not enough allowance is available.
+     *
+     * Might emit an {Approval} event.
+     */
+    function _spendAllowance(
+        address owner,
+        address spender,
+        uint256 amount
+    ) internal virtual {
+        uint256 currentAllowance = allowance(owner, spender);
+        if (currentAllowance != type(uint256).max) {
+            require(currentAllowance >= amount, "ERC20: insufficient allowance");
+            unchecked {
+                _approve(owner, spender, currentAllowance - amount);
+            }
+        }
+    }
+
+    /**
+     * @dev Hook that is called before any transfer of tokens. This includes
+     * minting and burning.
+     *
+     * Calling conditions:
+     *
+     * - when `from` and `to` are both non-zero, `amount` of ``from``'s tokens
+     * will be transferred to `to`.
+     * - when `from` is zero, `amount` tokens will be minted for `to`.
+     * - when `to` is zero, `amount` of ``from``'s tokens will be burned.
+     * - `from` and `to` are never both zero.
+     *
+     * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
+     */
+    function _beforeTokenTransfer(
+        address from,
+        address to,
+        uint256 amount
+    ) internal virtual {}
+
+    /**
+     * @dev Hook that is called after any transfer of tokens. This includes
+     * minting and burning.
+     *
+     * Calling conditions:
+     *
+     * - when `from` and `to` are both non-zero, `amount` of ``from``'s tokens
+     * has been transferred to `to`.
+     * - when `from` is zero, `amount` tokens have been minted for `to`.
+     * - when `to` is zero, `amount` of ``from``'s tokens have been burned.
+     * - `from` and `to` are never both zero.
+     *
+     * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
+     */
+    function _afterTokenTransfer(
+        address from,
+        address to,
+        uint256 amount
+    ) internal virtual {}
+
+    function toUint248(uint256 x) internal virtual returns (uint248) {
+        require(x < (1 << 248)); // signed, lim = bit-1
+        return uint248(x);
+    }
+}
```

### contracts/core/PendleMarket.sol
```diff
@@ -1,7 +1,7 @@
 // SPDX-License-Identifier: GPL-3.0-or-later
 pragma solidity 0.8.13;
 
-import "./PendleBaseToken.sol";
+import "./PendleERC20.sol";
 import "../interfaces/IPPrincipalToken.sol";
 import "../interfaces/ISuperComposableYield.sol";
 import "../interfaces/IPMarket.sol";
@@ -18,7 +18,7 @@ import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 // solhint-disable reason-string
 /// Invariances to maintain:
 /// - Internal balances totalPt & totalScy not interferred by people transferring tokens in directly
-contract PendleMarket is PendleBaseToken, PendleGauge, IPMarket {
+contract PendleMarket is PendleERC20, PendleGauge, IPMarket {
     using Math for uint256;
     using Math for int256;
     using MarketMathCore for MarketState;
@@ -32,8 +32,7 @@ contract PendleMarket is PendleBaseToken, PendleGauge, IPMarket {
         uint96 lastLnImpliedRate;
         uint96 oracleRate;
         uint32 lastTradeTime;
-        uint8 _reentrancyStatus;
-        // 1 SLOT = 232 bits
+        // 1 SLOT = 224 bits
     }
 
     uint8 private constant _NOT_ENTERED = 1;
@@ -46,27 +45,15 @@ contract PendleMarket is PendleBaseToken, PendleGauge, IPMarket {
     ISuperComposableYield internal immutable SCY;
     IPYieldToken internal immutable YT;
 
+    address public immutable factory;
+    uint256 public immutable expiry;
     int256 public immutable scalarRoot;
     int256 public immutable initialAnchor;
 
     MarketStorage public _storage;
 
-    modifier nonReentrant() {
-        // On the first call to nonReentrant, _notEntered will be true
-        require(_storage._reentrancyStatus != _ENTERED, "ReentrancyGuard: reentrant call");
-
-        // Any calls to nonReentrant after this point will fail
-        _storage._reentrancyStatus = _ENTERED;
-
-        _;
-
-        // By storing the original value once again, a refund is triggered (see
-        // https://eips.ethereum.org/EIPS/eip-2200)
-        _storage._reentrancyStatus = _NOT_ENTERED;
-    }
-
     modifier notExpired() {
-        require(!isExpired(), "market expired");
+        require(!_isExpired(), "market expired");
         _;
     }
 
@@ -77,7 +64,7 @@ contract PendleMarket is PendleBaseToken, PendleGauge, IPMarket {
         address _vePendle,
         address _gaugeController
     )
-        PendleBaseToken(NAME, SYMBOL, 18, IPPrincipalToken(_PT).expiry())
+        PendleERC20(NAME, SYMBOL, 18)
         PendleGauge(IPPrincipalToken(_PT).SCY(), _vePendle, _gaugeController)
     {
         PT = IPPrincipalToken(_PT);
@@ -87,7 +74,8 @@ contract PendleMarket is PendleBaseToken, PendleGauge, IPMarket {
         require(_scalarRoot > 0, "scalarRoot must be positive");
         scalarRoot = _scalarRoot;
         initialAnchor = _initialAnchor;
-        _storage._reentrancyStatus = _NOT_ENTERED;
+        expiry = IPPrincipalToken(_PT).expiry();
+        factory = msg.sender;
     }
 
     /**
@@ -321,6 +309,10 @@ contract PendleMarket is PendleBaseToken, PendleGauge, IPMarket {
         }
     }
 
+    function _isExpired() internal view virtual returns (bool) {
+        return block.timestamp >= expiry;
+    }
+
     function _writeState(MarketState memory market) internal {
         _storage.totalPt = market.totalPt.Int128();
         _storage.totalScy = market.totalScy.Int128();
@@ -342,17 +334,15 @@ contract PendleMarket is PendleBaseToken, PendleGauge, IPMarket {
         address from,
         address to,
         uint256 amount
-    ) internal override(ERC20, PendleGauge) {
-        // ERC20 by default does not have any hooks
+    ) internal override(PendleERC20, PendleGauge) {
         PendleGauge._beforeTokenTransfer(from, to, amount);
     }
 
     function _afterTokenTransfer(
         address from,
         address to,
         uint256 amount
-    ) internal override(ERC20, PendleGauge) {
-        // ERC20 by default does not have any hooks
+    ) internal override(PendleERC20, PendleGauge) {
         PendleGauge._afterTokenTransfer(from, to, amount);
     }
 }
```

### contracts/core/PendlePrincipalToken.sol
```diff
@@ -1,13 +1,15 @@
 // SPDX-License-Identifier: GPL-3.0-or-later
 pragma solidity 0.8.13;
 
-import "./PendleBaseToken.sol";
+import "./PendleERC20.sol";
 import "../interfaces/IPPrincipalToken.sol";
 import "../interfaces/IPYieldToken.sol";
 
-contract PendlePrincipalToken is PendleBaseToken, IPPrincipalToken {
+contract PendlePrincipalToken is PendleERC20, IPPrincipalToken {
     address public immutable SCY;
     address public immutable YT;
+    address public immutable factory;
+    uint256 public immutable expiry;
 
     modifier onlyYT() {
         require(msg.sender == address(YT), "ONLY_YT");
@@ -21,9 +23,11 @@ contract PendlePrincipalToken is PendleBaseToken, IPPrincipalToken {
         string memory _symbol,
         uint8 __decimals,
         uint256 _expiry
-    ) PendleBaseToken(_name, _symbol, __decimals, _expiry) {
+    ) PendleERC20(_name, _symbol, __decimals) {
         SCY = _SCY;
         YT = _YT;
+        expiry = _expiry;
+        factory = msg.sender;
     }
 
     /**
```

### contracts/core/PendleYieldToken.sol
```diff
@@ -1,15 +1,14 @@
 // SPDX-License-Identifier: GPL-3.0-or-later
 pragma solidity 0.8.13;
 
-import "./PendleBaseToken.sol";
+import "./PendleERC20.sol";
 import "../interfaces/ISuperComposableYield.sol";
 import "../interfaces/IPYieldToken.sol";
 import "../interfaces/IPPrincipalToken.sol";
 import "../libraries/math/Math.sol";
 import "../interfaces/IPYieldContractFactory.sol";
 import "../libraries/SCYUtils.sol";
 import "../SuperComposableYield/base-implementations/RewardManager.sol";
-import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 
 /*
@@ -20,7 +19,7 @@ It has been proven and tested that impliedScyBalance will not change over time,
 
 Due to this, it is required to update users' accruedReward STRICTLY BEFORE redeeming their interest.
 */
-contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, ReentrancyGuard {
+contract PendleYieldToken is PendleERC20, RewardManager, IPYieldToken {
     using Math for uint256;
     using SafeERC20 for IERC20;
 
@@ -41,6 +40,8 @@ contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, Reent
 
     address public immutable SCY;
     address public immutable PT;
+    address public immutable factory;
+    uint256 public immutable expiry;
 
     InterestState public interestState;
     mapping(address => UserInterest) public userInterest;
@@ -52,10 +53,12 @@ contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, Reent
         string memory _symbol,
         uint8 __decimals,
         uint256 _expiry
-    ) PendleBaseToken(_name, _symbol, __decimals, _expiry) {
+    ) PendleERC20(_name, _symbol, __decimals) {
         require(_SCY != address(0) && _PT != address(0), "zero address");
         SCY = _SCY;
         PT = _PT;
+        expiry = _expiry;
+        factory = msg.sender;
     }
 
     /**
@@ -162,7 +165,7 @@ contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, Reent
     /// @dev no reentrant & updateScyReserve since this function updates just the lastIndex
     function getScyIndex() public returns (uint256 currentIndex, uint256 lastIndexBeforeExpiry) {
         currentIndex = ISuperComposableYield(SCY).exchangeRateCurrent();
-        if (isExpired()) {
+        if (_isExpired()) {
             lastIndexBeforeExpiry = interestState.lastIndexBeforeExpiry;
         } else {
             lastIndexBeforeExpiry = currentIndex;
@@ -186,7 +189,7 @@ contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, Reent
 
         // minimum of PT & YT balance
         uint256 amountPYToRedeem = IERC20(PT).balanceOf(address(this));
-        if (!isExpired()) {
+        if (!_isExpired()) {
             amountPYToRedeem = Math.min(amountPYToRedeem, balanceOf(address(this)));
             _burn(address(this), amountPYToRedeem);
         }
@@ -258,7 +261,7 @@ contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, Reent
     /// @dev override the default updateRewardIndex to avoid distributing the rewards after
     /// YT has expired. Instead, these funds will go to the treasury
     function _updateRewardIndex() internal virtual override {
-        if (!isExpired()) {
+        if (!_isExpired()) {
             super._updateRewardIndex();
             return;
         }
@@ -326,6 +329,10 @@ contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, Reent
         interestState.scyReserve = IERC20(SCY).balanceOf(address(this)).Uint128();
     }
 
+    function _isExpired() internal view virtual returns (bool) {
+        return block.timestamp >= expiry;
+    }
+
     function _beforeTokenTransfer(
         address from,
         address to,
```

### contracts/core/actions/base/ActionSCYAndPYBase.sol
```diff
@@ -168,7 +168,8 @@ abstract contract ActionSCYAndPYBase is PendleJoeSwapHelperUpg {
         address SCY = IPYieldToken(YT).SCY();
 
         if (doPull) {
-            bool needToBurnYt = (!IPBaseToken(YT).isExpired());
+            bool isExpired = IPYieldToken(YT).expiry() <= block.timestamp;
+            bool needToBurnYt = (!isExpired);
             IERC20(PT).safeTransferFrom(msg.sender, YT, netPyIn);
             if (needToBurnYt) IERC20(YT).safeTransferFrom(msg.sender, YT, netPyIn);
         }
```

### contracts/interfaces/IPBaseToken.sol
```diff
@@ -1,9 +0,0 @@
-// SPDX-License-Identifier: GPL-3.0-or-later
-pragma solidity 0.8.13;
-import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
-
-interface IPBaseToken is IERC20Metadata {
-    function expiry() external view returns (uint256);
-
-    function isExpired() external view returns (bool);
-}
```

### contracts/interfaces/IPMarket.sol
```diff
@@ -1,12 +1,12 @@
 // SPDX-License-Identifier: GPL-3.0-or-later
 pragma solidity 0.8.13;
 
-import "./IPBaseToken.sol";
+import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
 import "./IPPrincipalToken.sol";
 import "./IPYieldToken.sol";
 import "../libraries/math/MarketMathCore.sol";
 
-interface IPMarket is IPBaseToken {
+interface IPMarket is IERC20Metadata {
     event AddLiquidity(
         address indexed receiver,
         uint256 lpToAccount,
```

### contracts/interfaces/IPPrincipalToken.sol
```diff
@@ -1,13 +1,17 @@
 // SPDX-License-Identifier: GPL-3.0-or-later
 pragma solidity 0.8.13;
-import "./IPBaseToken.sol";
+import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
 
-interface IPPrincipalToken is IPBaseToken {
+interface IPPrincipalToken is IERC20Metadata {
     function burnByYT(address user, uint256 amount) external;
 
     function mintByYT(address user, uint256 amount) external;
 
     function SCY() external view returns (address);
 
     function YT() external view returns (address);
+
+    function factory() external view returns (address);
+
+    function expiry() external view returns (uint256);
 }
```

### contracts/interfaces/IPYieldToken.sol
```diff
@@ -1,9 +1,9 @@
 // SPDX-License-Identifier: GPL-3.0-or-later
 pragma solidity 0.8.13;
-import "./IPBaseToken.sol";
+import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
 import "./IRewardManager.sol";
 
-interface IPYieldToken is IPBaseToken, IRewardManager {
+interface IPYieldToken is IERC20Metadata, IRewardManager {
     event RedeemRewards(address indexed user, uint256[] amountRewardsOut);
     event RedeemInterest(address indexed user, uint256 interestOut);
 
@@ -43,4 +43,8 @@ interface IPYieldToken is IPBaseToken, IRewardManager {
     function SCY() external view returns (address);
 
     function PT() external view returns (address);
+
+    function factory() external view returns (address);
+
+    function expiry() external view returns (uint256);
 }
```
