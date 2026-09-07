# [?] fix: potential deadlock issue. cs_wallet_manager_map should be locked after cs_wallet

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-07-10
Source: https://github.com/dashpay/dash/commit/8d5876ff99d12a42fd10cbd63466b590287f1fac
Type: security-commit

## Details
fix: potential deadlock issue. cs_wallet_manager_map should be locked after cs_wallet

 - Previous lock order was:
 -  (2) 'walletInstance->cs_wallet' in wallet/wallet.cpp:3191 (in thread 'httpworker.3')
 -  'cs_KeyStore' in wallet/scriptpubkeyman.cpp:1429 (in thread 'httpworker.3')
 -  (1) 'cs_wallet_manager_map' in coinjoin/walletman.cpp:145 (in thread 'httpworker.3')
 - Current lock order is:
 -  (1) 'cs_wallet_manager_map' in coinjoin/walletman.cpp:202 (in thread 'scheduler')
 -  'cs_deqsessions' in coinjoin/client.cpp:898 (in thread 'scheduler')
 -  (2) 'm_wallet->cs_wallet' in coinjoin/client.cpp:701 (in thread 'scheduler')
 -
