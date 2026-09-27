# [?] fixed: ioctl  node delegate crashes if ROLLDPOS not register (#2390) (#2398)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2020-08-20
Source: https://github.com/iotexproject/iotex-core/commit/97902627dc8d1e7af4b483de502acee829c12b26
Type: security-commit

## Details
fixed: ioctl  node delegate crashes if ROLLDPOS not register (#2390) (#2398)

* fixed: ioctl  node delegate crashes if ROLLDPOS not register (#2390)

In standalone mode or no consensus configurations mode, `ioctl node delegate` or `ioctl node probationlist` will crash cause no consensus registered.

* assign value to epochNum

Co-authored-by: dustinxie <dahuaxie@gmail.com>
