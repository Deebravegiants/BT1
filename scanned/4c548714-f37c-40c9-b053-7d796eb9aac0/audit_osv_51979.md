# [M] CVE-2021-46921

## Summary
Severity: Medium
Advisory: CVE-2021-46921
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46921
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

locking/qrwlock: Fix ordering in queued_write_lock_slowpath()

While this code is executed with the wait_lock held, a reader can
acquire the lock without holding wait_lock.  The writer side loops
checking the value with the atomic_cond_read_acquire(), but only truly
acquires the lock when the compare-and-exchange is completed
successfully which isn’t ordered. This exposes the window between the
acquire and the cmpxchg to an A-B-A problem which allows reads
following the lock acquisition to observe values speculatively before
the write lock is truly acquired.

We've seen a problem in epoll where the reader does a xchg while
holding the read lock, but the writer can see a value change out from
under it.

  Writer                                | Reader
  --------------------------------------------------------------------------------
  ep_scan_ready_list()                  |
  |- write_lock_irq()                   |
      |- queued_write_lock_slowpath()   |
	|- atomic_cond_read_acquire()   |
				        | read_lock_irqsave(&ep->lock, flags);
     --> (observes value before unlock) |  chain_epi_lockless()
     |                                  |    epi->next = xchg(&ep->ovflist, epi);
     |                                  | read_unlock_irqrestore(&ep->lock, flags);
     |                                  |
     |     atomic_cmpxchg_relaxed()     |
     |-- READ_ONCE(ep->ovflist);        |

A core can order the read of the ovflist ahead of the
atomic_cmpxchg_relaxed(). Switching the cmpxchg to use acquire
semantics addresses this issue at which point the atomic_cond_read can
be switched to use relaxed semantics.

[peterz: use try_cmpxchg()]

## References
- https://git.kernel.org/stable/c/5902f9453a313be8fe78cbd7e7ca9dba9319fc6e
- https://git.kernel.org/stable/c/82808cc026811fbc3ecf0c0b267a12a339eead56
- https://git.kernel.org/stable/c/82fa9ced35d88581cffa4a1c856fc41fca96d80a
- https://git.kernel.org/stable/c/84a24bf8c52e66b7ac89ada5e3cfbe72d65c1896
- https://git.kernel.org/stable/c/d558fcdb17139728347bccc60a16af3e639649d2
