# [?] Fix GCS crash when a field APDU arrives during an active review

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-08-07
Source: https://github.com/LedgerHQ/app-ethereum/commit/e0c4bc997b2e8fb1d74753b025f38102990cb79d
Type: security-commit

## Details
Fix GCS crash when a field APDU arrives during an active review

When handle_field() is invoked in SIGNING_TX state but get_current_tx_info()
returns NULL, it was calling gcs_cleanup() before returning
SWO_COMMAND_NOT_ALLOWED.

gcs_cleanup() frees g_pairs and g_pairsList. If a GCS review is
currently shown on screen, NBGL still holds pointers into those buffers
and dereferences them the next time it redraws the page, causing a SIGSEGV.

The cleanup is not needed at this site: when no tx_info is registered,
nothing has been allocated for this field session yet. If a review is
active, the proper cleanup happens in the approve/reject callbacks and
in reset_app_context(), which already calls ui_idle() before
ui_all_cleanup() so NBGL always drops its references first.
