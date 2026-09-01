# [?] security: land the coordinated security patch set on master (#8997)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-13
Source: https://github.com/fedimint/fedimint/commit/85e47fe4f6f77896e3e06ed0ca1701d646b8e9ab
Type: security-commit

## Details
security: land the coordinated security patch set on master (#8997)

## Summary

This lands the coordinated security patch set on `master`: 30 commits
hardening the Lightning (LNv1/LNv2), wallet, gateway and server modules
against unauthenticated or unvalidated inputs that could crash a
guardian, corrupt consensus, or let a peer claim funds it does not own.
Each commit is self-contained, carries its own rationale in the commit
message, and is rebased onto the current `master` tip.

## Disclosure status

All known federations have been contacted and are already updated, so
these fixes are being landed in the open.

## Details

The patches fall into a few groups:

**Contract funding and claiming (LNv1/LNv2).** Incoming contracts could
be funded more than once, funded with a ciphertext that no offer commits
to, or funded with a caller-chosen decryption outcome. The last of these
is the most damaging: the resulting decryption-share key is never
consumed, so every guardian re-emits a consensus item for it once per
second for the life of the federation, and nothing short of a migration
removes it. The fixes reject duplicate funding, bind the ciphertext to
its offer, and require a pending decryption at funding time.

**Consensus version gating.** Three of the new rules cannot be applied
unconditionally: pre-existing sessions accepted the inputs they now
reject and must replay identically, and an ungated rejection would split
upgraded from un-upgraded peers on an ordered item mid-upgrade. LNv1
therefore gains the consensus-version voting mechanism already used by
walletv1, and the new rules activate at LN consensus version 2.1/2.3 and
wallet 2.3.

**Panic containment.** Several API and consensus paths could be driven

_Trimmed to 38 lines — full report: https://github.com/fedimint/fedimint/commit/85e47fe4f6f77896e3e06ed0ca1701d646b8e9ab_
