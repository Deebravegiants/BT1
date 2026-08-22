# [?] Added SharedMutex lock to sync.h, plus fixed deadlock detector 

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-11-27
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/fdfe72acc49ca722315db72bc637e079eaef7379
Type: security-commit

## Details
Added SharedMutex lock to sync.h, plus fixed deadlock detector 

Co-authored-by: Griffith probablyaplebeian@protonmail.com

Summary
-------

While investigating other issues, I noticed that our thread safety system
is missing any notion of a shared mutex (read-write lock).
As such, I went ahead and added it to our thread safety/annotations system.

Motivation:
We may need this in the future. Shared mutexes are very useful and
it pays to have them incorporated into our thread-safety system.
I also went ahead and backported from ABC the core backport that adds the
REVERSE_LOCK macro. This is ABC D6532 I also noticed that our thread safety
stuff that runs in debug mode is quite handy for detecting deadlocks, but
the error message it prints is slightly incorrect (it confuses
"previous lock order" with "current lock order").

I created an issue for this: #316. This closes #316.

Additionally, as described in issue #323, our deadlock detection code is
unable to detect cycles of the form:

Thread 1: Locks A, B
Thread 2: Locks B, C
Thread 3: Locks C, A

The above situation has been addressed in this MR, thus this closes #323.

This MR has the following changes:

- Backport of ABC D6532 (adding the REVERSE_LOCK macro).
- Fix the error message when potential_deadlock_detected fires
  (requires Debug build). The error message reversed previous and
  current lock order. Closes #316.
- Detect deadlock cycles involving more than 2 threads. Closes #323.

_Trimmed to 38 lines — full report: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/fdfe72acc49ca722315db72bc637e079eaef7379_
