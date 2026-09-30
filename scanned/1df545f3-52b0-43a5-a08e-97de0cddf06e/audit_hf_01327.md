# [M] M-1 WalletUpgradable initialization is risky

## Summary
Severity: Medium
Contest weight: 0.0525
Dataset id: 6590
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the initialization process of an upgradable wallet that relies on a proxy contract. In the current design the proxy is initially owned by an external administrator and the wallet’s constructor performs several setup steps, after which the admin must manually transfer ownership of the proxy to the wallet contract to complete the initialization. This hand‑off creates a window of risk because the external admin retains full control over the proxy until the transfer occurs. If the admin never performs the transfer, or if the transfer is performed to an address controlled by an attacker, the attacker can invoke the upgrade mechanism of the proxy and replace the wallet logic with a malicious implementation. Consequently the attacker could redirect withdrawals, freeze the wallet, or otherwise compromise the funds held by the wallet. The issue manifests whenever a new wallet is deployed through the existing factory but the factory does not enforce the final ownership transfer; it depends on an off‑chain step that may be omitted or tampered with. Users of the wallet, the wallet owners, and any protocol that relies on the wallet’s security are affected because they may lose control over their assets without any visible warning. The problem was identified during a manual audit that highlighted the multi‑step initialization and the reliance on an external admin for the final ownership change. It is easy to miss because the ownership transfer is a separate transaction that does not appear in the constructor code, and the proxy’s admin role is not visibly linked to the wallet’s address in the source. To remediate the issue the wallet should be instantiated using a factory pattern that automatically sets the proxy’s admin to the wallet itself, eliminating the need for a manual hand‑off. Alternatively, the contract can adopt the UUPSUpgradeable pattern with a properly restricted _authorizeUpgrade function that only allows upgrades when called by the wallet contract itself (onlySelfCall), ensuring that no external party can hijack the upgrade path. By guaranteeing that the proxy is owned by the wallet from the moment of deployment, the risk of unauthorized upgrades and fund loss is removed.

## Recommendation
We recommend applying the same factory-pattern for wallets as well in order to guarantee correct ﬁnalized initialization.
Also one of the solutions is to use UUPSUpgradeable with the correct setting _authorizeUpgrade() method via onlySelfCall.
