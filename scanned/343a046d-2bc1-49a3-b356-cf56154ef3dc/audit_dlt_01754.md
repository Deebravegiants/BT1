# [?] fix(client): fix overflow in get_extra_sync_block_hashes() (#11670)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-06-27
Source: https://github.com/near/nearcore/commit/fc3c82c771e2612f1cd2c8f896303dfcf5aa9d9b
Type: security-commit

## Details
fix(client): fix overflow in get_extra_sync_block_hashes() (#11670)

Subtracting 1 from the smallest chunk height included crashes when it's
zero, which can actually happen in many tests, and is currently causing
the skip_epoch.py test to fail
