# [?] fix: deadlock while racing `ipfs dag import` and `ipfs repo gc`

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2023-03-25
Source: https://github.com/ipfs/kubo/commit/bb020ea1ef8765f873e06ae4fd7f58c075b04edc
Type: security-commit

## Details
fix: deadlock while racing `ipfs dag import` and `ipfs repo gc`

This fixes a deadlock introduced in 1457b4fd4abff0bdcdccbacc26934cb7fa8e8a43.

We can't use the coreapi here because it will try to take the PinLock (RLock) again, so revert this small part of 1457b4fd4abff0bdcdccbacc26934cb7fa8e8a43.

This used cause a deadlock when concurrently running `ipfs dag import` concurrently with the GC.

The bug is that `ipfs dag import` takes an RLock with the PinLock.
*the cars are imported, leaving a wide window of time*
Then GC Takes a Lock on that same RWMutex while taking the GC Lock (it  blocks because it waits for the RLock to be released).
Then the car imports are finished and `ipfs dag import` tries to aqcuire the PinLock (doing an RLock) again in `Api().Pin`.

However at this point the RWMutex is starved, the runtime put a fence in front of RLocks if a Lock has been waiting for too lock (else you could have an endless stream of RLock / RUnlock forever delaying a Lock to ever go through).

The issue is that `ipfs dag import`'s original RLock which is blocking everyone will be released once it returns, which only happens when `Api().Pin` completes.

So we have a deadlock (ABA kind ?), because `ipfs dag import` waits on the GC Lock, which waits on `ipfs dag import`.

Calling the Pinner directly does not acquire the PinLock again, and thus does not have this issue.
