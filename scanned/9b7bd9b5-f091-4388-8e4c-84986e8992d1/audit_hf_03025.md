# [M] function changeController

## Summary
Severity: Medium
Contest weight: 0.2547
Dataset id: 16908
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a privileged upgrade path that allows the contract admin (or any address with factory privileges) to replace the controller address of every vault deployed by the protocol at will. The function that performs this replacement, typically named changeController, does not enforce any delay, multi‑signature governance, or user notification, and it can be called by a single privileged account at any time. The root cause is an overly centralized access control model: the controller, which is the only entity authorised to invoke the withdraw‑like function sendTokens, can be arbitrarily reassigned without any safeguard. An attacker who gains control of the admin key, or a malicious insider, can call changeController to point the vaults to a contract under their control, and subsequently invoke sendTokens for each vault identifier. Because sendTokens is guarded only by the onlyController modifier, the malicious controller can transfer the full token balance (idFinalTVL) of each vault to an address of the attacker’s choosing. The impact is a complete loss of user‑deposited assets: users who have deposited tokens into any vault will see their balances drop to zero, withdrawals will fail, and any expectation of a refundable or earn‑back amount is violated. This scenario can happen at any moment after a vault is created, without any warning or on‑chain notice to users. All participants who rely on the vaults – individual depositors, liquidity providers, and the protocol that advertises safe custody – are affected. The issue was discovered during a manual audit and code review, where the absence of timelocks, events, or multi‑sig checks around the controller change function was identified as a design weakness. The bug is difficult to notice in normal operation because the ability to change the controller is presented as a legitimate upgrade mechanism, and there are no visible red flags in the UI; the vault’s interface continues to display the deposited amount until the malicious controller executes the transfer, at which point the user’s balance appears to vanish instantly. The vulnerability belongs to the class of “centralised privileged function” or “upgradeability backdoor” bugs that enable a rug‑pull by a single authority. To remediate, the protocol should restrict controller changes to a secure, transparent process – for example, moving the changeController logic to a factory contract behind a multi‑signature timelocked governance, emitting an explicit event on every change, and optionally making the controller immutable after an initial upgrade window. By enforcing a delay and community oversight, users are given the opportunity to withdraw their funds before a malicious controller can be installed, thereby preserving the intended accounting guarantees of the vault system.

## Proof of Concept
Controller can be changed by admin anytime without any warning to users.

[Vault.sol#L295](https://github.com/code-423n4/2022-09-y2k-finance/blob/2175c044af98509261e4147edeb48e1036773771/src/Vault.sol#L295)
    
    function changeController(address _controller) public onlyFactory {
        if(_controller == address(0))
            revert AddressZero();
        controller = _controller;
    }

Tokens in the vaults can then be called by the malicious contract to be transferred to their own address with `sendTokens()`.

[Vault.sol#L360-L366](https://github.com/code-423n4/2022-09-y2k-finance/blob/2175c044af98509261e4147edeb48e1036773771/src/Vault.sol#L360-L366)
    
    function sendTokens(uint256 id, address _counterparty)
        public
        onlyController
        marketExists(id)
    {
        asset.transfer(_counterparty, idFinalTVL[id]);
    }

## Recommendation
Allow the change of controller address only in the `VaultFactory()`. This way, markets that have been created cannot have a different controller address, so users can be made aware of the change before choosing to make deposit of assets.

Implemented timelock as issued in another finding.

Admin privilege finding, rationale for QA explained [here](https://github.com/code-423n4/2022-09-y2k-finance-findings/issues/49#issuecomment-1295781746)

Hi @HickupHH3. Would like to seek clarifications on why this was downgraded to QA. In the rationale given, “Those that explained the impact and vulnerability in detail will be grouped together with medium severity “.

I believe the way a compromised admin can rug is clear in this report. `changeController()` can be used to change controller to any address. This address can then be used to call `sendTokens()` to steal all assets in every vault.

Took another look at this.

I disagree with the recommended fix. The purpose for having the controller changeable in the deployed instances is well intentioned for upgradeability purposes: perhaps new features are to be added to the controller, and migration to a new controller for all existing vaults is required to incur less technical debt. Needing to maintain legacy controllers isn’t great from a devops POV.

That said, based on my rationale, the issue should stand as a medium severity issue until we have the introduction of centralisation reports. Kenzo said it well:

IMO most of these trusted-actor issues basically just describe general properties of the crypto/governance ecosystems, and do not reflect a novel problem in the design/implementation (which wardens are paid to discover). Because of this, and because of the circular logic, I believe we should change the rules and add a dedicated centralization report.
