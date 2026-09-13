# [?] qt: Preventing a crash using "window" menu during application start-up

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-03-13
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/d836e896ecc743514a7f484f974988bd3d2e367e
Type: security-commit

## Details
qt: Preventing a crash using "window" menu during application start-up

This commit fixes a bug introduced into
459b3bb5d02a8deed9456ff9087f3c5b3e4e88e1: qt: Add Window menu Some options in
the menu are enabled while the node is initializing, and can lead to a crash if
selected by the user.

The issue was reproduced and fixed on OSX, but the problem seems
platform-independent.

**How to reproduce**

* Run BitcoinCashNode-Qt
* While the application is starting-up, go into the 'Window' menu, and select
  'Console traffic'
* The application will crash

**What this fixes**

The menu items are disabled while the application is initializing, and enabled
once the initialization is over.

**How to test**

* Run BitcoinCashNode-Qt
* While the application is starting-up, go into the 'Window' menu, see that the
  items 'Main window', 'Information', 'Console', 'Network traffic' and 'Peers'
  are disabled.
* Once the splash window vanishes, these items are enabled.
