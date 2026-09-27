# [M] Blacklisted USDE holder can conver his USDE into invest coin shares by  depositing shares to a whitelisted account

## Summary
Severity: Medium
Chain: Smart contract
Component: Euro-Dollar
Published: 2024-11-05
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/58
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x8ecbf047e90107416f976c7c31be94d3357161e748b78e2245043178f21ff4d8
**Severity:** medium

**Description:**
**Description**\

The impact here is, a whitelisted suer can still be taking part in using USDE or gain invest coin’s yield. Which he shouldn’t be.

An account with blacklisted status can avoid locking his USDE forever, by burning the USDE for invest coin shares and redeem the shares on different account. There by avoiding the blacklisted status. He can not only unlock his USDE but invest on invest coin and generate yield.

Root cause : the invest coin.deposit function burns the USDE from `msg.sender` without checking if it is blacklisted.

Mitigation : check if `msg.sender` blacklisted on `InvestToken.deposit`

**Attack Scenario**\

1. Blacklister will blacklist a user, so he cannot transfer or receive USDE anymore

2. But, as soon as blacklisted, in the next block itself, he will call `InvestToken.deposit` with his entire USDE balance and receiver as a new account that is whitelisted. That receiver will get mint the shares at current price.

3. Then the receiver which is his new account can redeem the shares or transfer the shares to any new account that is WHITELISTED.

4. Then they can redeem shares into USDE and use the USDE, or if blacklister still blacklists this new account/receiver, shares can be redeemed to a WHITELISTED account + sell USDE for other stablecoin in a single transaction and avoid being rekt by blacklisting and custom burning process by admins.

5. Or doing no transfer of shares, he can wait to generate yield, then redeem the shares by burning invest coin shares, and receive USDE on a new void/whitelisted account

https://github.com/eurodollar-fi/eurodollar-protocol/blob/3900ae6a01f5c60146d314bf45b2ab67179422d1/src/InvestToken.sol#L243

```solidity

InvestToken.sol
245:     function deposit(uint256 assets, address receiver) public returns (uint256 shares) {
246:         shares = convertToShares(assets);
247:         usde.burn(msg.sender, assets);
248:         _mint(receiver, shares);
249: 
250:         emit Deposit(msg.sender, receiver, assets, shares);
251:     }


Validator.sol
130:     function isValid(address from, address to) external view returns (bool valid) {
131:         return accountStatus[from] == Status.BLACKLISTED ? to == address(0x0) : accountStatus[to] != Status.BLACKLISTED;
132:     }


USDE.sol
81:     function _update(
82:         address from,
83:         address to,
84:         uint256 amount
85:     )
86:         internal
87:         override(ERC20Upgradeable, ERC20PausableUpgradeable)
88:     {
89:  >>    require(validator.isValid(from, to), "account blocked");
90: 
91:         super._update(from, to, amount);
92:     }

112:     function burn(address from, uint256 amount) public onlyRole(BURN_ROLE) returns (bool) {
113:         _burn(from, amount);
114: 
115:         return true;
116:     }

```

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
