# [M] Malicious users can front-run to cause a denial of service

## Summary
Severity: Medium
Contest weight: 0.3252
Dataset id: 19405
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an economic denial‑of‑service that arises when a malicious actor can transfer USDe tokens directly into the StakedUSDe contract without invoking the deposit function. The contract calculates the number of shares to mint using a formula that divides the amount of assets by the total assets held by the contract (totalAssets) plus a constant, and then checks that the resulting share amount is at least a minimum threshold (MIN_SHARES = 1 ether). Because totalAssets is derived from the token balance of the contract, a direct transfer increases the denominator while the totalSupply of shares remains unchanged. This dilution makes the share conversion factor arbitrarily small. When the attacker sends a small amount, for example 1 ether, the next legitimate user attempting to deposit any reasonable amount receives fewer than the required minimum shares, causing the deposit call to revert with a MinSharesViolation error. The impact is that legitimate users are unable to stake USDe, their transactions fail, and the protocol becomes effectively unusable, constituting a denial of service. The condition occurs whenever the contract permits arbitrary ERC20 transfers into its balance and enforces a non‑zero minimum share requirement. All users who try to deposit after the malicious transfer are affected, while existing share holders retain their balances but cannot receive new shares. The issue was discovered during a Code4rena audit by constructing a test that performed a direct token transfer followed by a normal deposit, which consistently reverted. The problem is subtle because the token transfer itself does not revert and the share calculation appears correct under normal operation; only the interaction between external balance changes and the minimum‑share guard reveals the flaw. From a user perspective the symptom is a transaction that reverts with an obscure “MinSharesViolation” error, leaving the user with no new shares and an unchanged token balance, contrary to the expectation that a deposit of thousands of ether would succeed. This bug belongs to the class of share‑dilution or accounting‑invariant violations that enable front‑run denial‑of‑service attacks. To remediate the issue the contract should either enforce a minimum deposit amount that cannot be bypassed by external transfers, prevent direct token transfers into the contract, or redesign the share calculation to rely on an internal accounting variable rather than the raw token balance, thereby eliminating the possibility of share dilution and ensuring that the minimum‑share check does not unintentionally block legitimate deposits.

## Proof of Concept
User deposit `USDe` token to `StakedUSDe` protocol to get share via invoke external `deposit` function. Let’s see how share is calculate:
    
    function _convertToShares(uint256 assets, Math.Rounding rounding) internal view virtual returns (uint256) {
        return assets.mulDiv(totalSupply() + 10 ** _decimalsOffset(), totalAssets() + 1, rounding);
    }

Since `decimalsOffset() == 0` and totalAssets equal the balance of `USDe` in this protocol
    
    function totalAssets() public view virtual override returns (uint256) {
        return _asset.balanceOf(address(this));
    }

$$ f(share) = (USDeAmount \ast totalSupply) / (totalUSDeAssets() + 1) $$ 

The minimum share is set to 1 ether.
    
    uint256 private constant MIN_SHARES = 1 ether;

Assuming malicious users transfer 1 ether of `USDe` into the protocol and receive ZERO shares, how much tokens does the next user need to pay if they want to exceed the minimum share limit of 1 ether? That would be 1 ether times 1 ether, which is a substantial amount.

I add a test case in `StakedUSDe.t.sol`:
    
    function testMinSharesViolation() public {
        address malicious = vm.addr(100);

        usdeToken.mint(malicious, 1 ether);
        usdeToken.mint(alice, 1000 ether);

        //assume malicious user deposit 1 ether into protocol.
        vm.startPrank(malicious);
        usdeToken.transfer(address(stakedUSDe), 1 ether);

        vm.stopPrank();
        vm.startPrank(alice);
        usdeToken.approve(address(stakedUSDe), type(uint256).max);

        //1000 ether can't exceed the minimum share limit of 1 ether
        vm.expectRevert(IStakedUSDe.MinSharesViolation.selector);
        stakedUSDe.deposit(1000 ether, alice);
    }

We can see even Alice deposit a substantial number of tokens but still cannot surpass the 1 ether share limit which will lead to a denial of service (DoS) for StakedUSDe due to MinShares checks.

## Recommendation
We can solve this issue by setting a minimum deposit amount.
