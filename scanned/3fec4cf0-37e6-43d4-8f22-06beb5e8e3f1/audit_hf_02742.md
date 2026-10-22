# [M] Disabled Adapters Should Stay Disabled

## Summary
Severity: Medium
Contest weight: 0.0388
Dataset id: 15011
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a permission‑logic flaw that allows any address to re‑enable an adapter that has previously been disabled through the whenPermissionless entry point. The root cause is that the contract does not keep a permanent record that an adapter has been removed, nor does it enforce a check that prevents a disabled adapter from being added again. An attacker can simply call the enable function after a legitimate disable action, causing the adapter to become active again without any governance or owner approval. This can be exploited by observing a transaction that disables an adapter—often done for security or upgrade reasons—and then immediately submitting a transaction that calls the same function to add the adapter back. Because the enable function is permissionless, the attacker does not need any special role. The impact is that the protocol’s intended safety barrier is bypassed; a compromised or malicious adapter can be re‑introduced, potentially allowing unauthorized token transfers, price manipulation, or other harmful actions that affect all users and the overall integrity of the system. The issue manifests whenever an adapter is disabled in a permissionless context; under those conditions the contract’s state machine treats the adapter as if it were never removed. Users may notice that an adapter they thought was disabled suddenly appears active again in the UI, leading to unexpected behavior such as transactions being routed through a faulty module or funds being processed by a contract that should no longer be trusted. The bug was discovered during a manual security review that examined the lifecycle management of adapters and identified the missing guard. It can be hard to notice because the enable function works correctly for fresh adapters, so the re‑enable path looks identical to a normal addition, masking the fact that a previously disabled component has been resurrected. To remediate, the contract should maintain an immutable “removed” flag for each adapter and reject any attempt to add an adapter that has been marked as removed, or require explicit governance approval for re‑adding. This change restores the intended invariant that once an adapter is disabled, it stays disabled unless a privileged process explicitly overrides the restriction, thereby aligning the implementation with the protocol’s security model and preventing accidental or malicious re‑activation of unsafe modules.

## Recommendation
Don’t allow an adapter that has been removed (i.e. it was active and it is being disabled) to be re-added.
As discussed, this is the preferred solution of the Sense team.
