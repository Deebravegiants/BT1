# [?] fix: crash in mnemonicverificationdialog by proper using reject() event

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-02-02
Source: https://github.com/dashpay/dash/commit/c24473b99d698b7a4c75b70f5b833824c5e23e96
Type: security-commit

## Details
fix: crash in mnemonicverificationdialog by proper using reject() event

This call disconnect(cancel, nullptr, nullptr, nullptr) for cancel makes
an internal slots disconnected and it could cause objects to get
invalid internal state at some point if theme is changed.
