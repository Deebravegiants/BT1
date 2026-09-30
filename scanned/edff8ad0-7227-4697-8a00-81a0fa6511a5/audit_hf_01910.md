# [M] specify gas limit to the mailbox

## Summary
Severity: Medium
Contest weight: 0.0507
Dataset id: 10503
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability isa missing or incorrect gas limit configuration for cross‑chain messages sent through the Hyperlane mailbox. The contract’s metadata function, which should specify the amount of gas that the destination chain must allocate for processing an incoming message, is left unchanged, causing the system to fall back to a hard‑coded default of 50,000 gas. This default is documented but is insufficient once the destination chain’s epoch increases and the execution cost of the message grows. The root cause is a failure to override the metadata function with a value that reflects the actual gas requirements of the target contract, combined with the use of an older Hyperlane version where the gas limit is hidden inside the metadata rather than being an explicit argument. An attacker does not need to actively exploit the bug; the issue manifests automatically when a legitimate user sends a message that requires more than the default gas. The message execution then reverts or is dropped, leading to a situation where the sender receives no confirmation, the UI shows no response, and any funds attached to the message appear to disappear or become locked. This impacts any user or protocol that relies on Hyperlane for cross‑chain communication, especially those that have upgraded the destination contract or whose epoch has progressed, because the gas consumption of the destination logic has risen. The problem was discovered during a manual audit that compared the contract code against Hyperlane documentation and noted the absence of a custom metadata implementation. It can be hard to notice because the default gas limit is large enough for early deployments, so the failure only surfaces later, often after a protocol upgrade or a change in the destination contract’s complexity. To remediate, the metadata function should be overridden to return a gas limit that matches the destination’s actual needs, and the project should consider upgrading to a newer Hyperlane version where the gas limit is passed as an explicit argument, making the requirement obvious and reducing the chance of omission. Conceptually, this is a configuration‑parameter omission bug that violates the assumption that the destination chain will always have enough gas to execute the incoming message, breaking the accounting model that expects every cross‑chain call to succeed and funds to be transferred reliably.

## Recommendation
Overwrite the function with the correct metadata. Additionally, the Hyperlane version used
is old, consider using a more recent one. In the newer version, metadata is sent as an
argument, which makes it more obvious that it must be set.
