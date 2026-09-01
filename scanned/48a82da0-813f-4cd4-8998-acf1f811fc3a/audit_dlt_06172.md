# [H] gimmeToken function does not check that the contract has pre-funded wxHopr

## Summary
Severity: High
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-13
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/39
Type: hats-finding

## Details
**Github username:** @ololade97
**Submission hash (on-chain):** 0x18511f52b4d81273bbf1d977c649b29aaf4e0388eacf89eb442f5542f4b15724
**Severity:** high

**Description:**
**Description**

- User's attempt to claim their staking rewards will fail unexpectedly.
- User may not realize why it failed or that the contract needed to be funded first.
- User may repeatedly try claiming without success, wasting gas fees
- The intended reward transfer will not occur as expected


**Attack Scenario**\
Describe how the vulnerability can be exploited.

**Attachments**
https://github.com/hoprnet/hoprnet/blob/274b59e409e6bf48c6d7d675de2d9905dcf1f813/packages/ethereum/contracts/src/static/stake/HoprWhitehat.sol


1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
function gimmeToken() external nonReentrant {
    require(isActive, 'Whitehat is not active');
    // ensure STEP 1
    require(myHoprStake.owner() == address(this), 'HoprStake needs to transfer ownership');
    // ensure STEP 2
    require(
      ERC1820_REGISTRY.getInterfaceImplementer(msg.sender, TOKENS_RECIPIENT_INTERFACE_HASH) == address(this),
      'Caller has to set this contract as ERC1820 interface'
    );

    // store caller to be used throughout the call
    currentCaller = msg.sender;
    // updates the rewards inside the accounts mapping struct
    myHoprStake.sync(currentCaller);

    (

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/39_
