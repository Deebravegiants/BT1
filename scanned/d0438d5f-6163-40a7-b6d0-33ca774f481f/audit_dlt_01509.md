# [?] easylogging++: fix potential memory corruption

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-02-13
Source: https://github.com/monero-project/monero/commit/8889f490ce8e4fc0e7f7b9c47f8ef46f5a509cf3
Type: security-commit

## Details
easylogging++: fix potential memory corruption

The m_typedConfigurations pointer is copied from one object to the next,
but deleted in the dtor, leading to potential double free. It is also
deleted first thing in the copy ctor, deleting uninitialized memory.

This does not seem to actually happen in practice (those functions do
not get called), but seems safer that way.

Coverity 1446562
