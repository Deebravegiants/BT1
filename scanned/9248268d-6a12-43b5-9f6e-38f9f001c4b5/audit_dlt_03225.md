# [M] Approved gscApprove allowance to an address may not able to be decreased

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-25
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/58
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/ArcadeTreasury.sol#L189-L201


# Vulnerability details

## Impact
Approved gscApprove allowance to an address may not able to be decreased.

## Proof of Concept
**GSC_CORE_VOTING_ROLE** calls [gscApprove(...)]() function to approve tokens to be pulled from the treasury:
```
    function gscApprove(
        address token,
        address spender,
        uint256 amount
    ) external onlyRole(GSC_CORE_VOTING_ROLE) nonReentrant {
        if (spender == address(0)) revert T_ZeroAddress("spender");
        if (amount == 0) revert T_ZeroAmount();


        // Will underflow if amount is greater than remaining allowance
        gscAllowance[token] -= amount;


        _approve(token, spender, amount, spendThresholds[token].small);
    }
```
Each approval will decrease the `gscAllowance[token]` by the approved allowance amount, this is problematic as **GSC_CORE_VOTING_ROLE** may not able to decrease the approved allowance.

Consider the following scenario:
1. `gscAllowance[token]` is 100;
2. **GSC_CORE_VOTING_ROLE** calls **gscApprove(...)** to give 60 allowance to a third party;
3. `gscAllowance[token]` is 40 now;
4. Later **GSC_CORE_VOTING_ROLE** finds the approved allowance is a bit too high and want to decrease the allowance to 50;
5. **gscApprove(...)** is called again but the ransaction reverts due to underflow error (`gscAllowance[token]` is less than 50)

Please see the tests:
```
contract ArcadeTreasuryTest is Test {
    address timelock = address(1);
    address coreVoting = address(2);
    address gscCoreVoting = address(3);
    address other = address(4);

    ArcadeTreasury treasury;
    MockToken mockToken;

    function setUp() public {
        treasury = new ArcadeTreasury(timelock);

        vm.startPrank(timelock);
        treasury.grantRole(treasury.CORE_VOTING_ROLE(), coreVoting);
        treasury.grantRole(treasury.GSC_CORE_VOTING_ROLE(), gscCoreVoting);

        mockToken = new MockToken("Mock Token", "MT");
        IArcadeTreasury.SpendThreshold memory threshold = IArcadeTreasury.SpendThreshold(100 ether, 200 ether, 300 ether);
        treasury.setThreshold(address(mockToken), threshold);
        vm.stopPrank();
    }

    function testGscApprove() public {
        vm.warp(7 days);

        vm.prank(timelock);
        treasury.setGSCAllowance(address(mockToken), 100 ether);

        vm.startPrank(gscCoreVoting);
        treasury.gscApprove(address(mockToken), address(4), 60 ether);
        vm.expectRevert(stdError.arithmeticError);
        treasury.gscApprove(address(mockToken), address(4), 50 ether);
        vm.stopPrank();
    }
}

contract MockToken is ERC20 {
    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {}

    function mint(address account, uint256 amount) public {
        _mint(account, amount);
    }
}
```

## Tools Used
Manual Review

## Recommended Mitigation Steps
When approve to a particular address, compare the new allowance with current allowance ([IERC20.allowance(...)](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/7222a31d548695998a475c9661fa159ef45a0e88/contracts/token/ERC20/IERC20.sol#L50)):
1. If the current allowance is equal to new allowance, do nothing;
2. If the current allowance is less than new allowance, `gscAllowance[token] -= (new allowance - current allowance)`;
3. IF the current allowance is larger than new allowance, `gscAllowance[token] += (current allowance - new allowance)`.



## Assessed type

Access Control
