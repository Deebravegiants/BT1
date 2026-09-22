# [H] eventpoll: don't decrement ep refcount while still holding the ep mutex

## Summary
Severity: High
Advisory: CVE-2025-38349
Aliases: A-432751421, ASB-A-432751421
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-18
Source: https://osv.dev/vulnerability/CVE-2025-38349
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.178, >=6.2.0 <6.6.99, >=6.4.0 <6.12.39, >=6.7.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

eventpoll: don't decrement ep refcount while still holding the ep mutex

Jann Horn points out that epoll is decrementing the ep refcount and then
doing a

    mutex_unlock(&ep->mtx);

afterwards. That's very wrong, because it can lead to a use-after-free.

That pattern is actually fine for the very last reference, because the
code in question will delay the actual call to "ep_free(ep)" until after
it has unlocked the mutex.

But it's wrong for the much subtler "next to last" case when somebody
*else* may also be dropping their reference and free the ep while we're
still using the mutex.

Note that this is true even if that other user is also using the same ep
mutex: mutexes, unlike spinlocks, can not be used for object ownership,
even if they guarantee mutual exclusion.

A mutex "unlock" operation is not atomic, and as one user is still
accessing the mutex as part of unlocking it, another user can come in
and get the now released mutex and free the data structure while the
first user is still cleaning up.

See our mutex documentation in Documentation/locking/mutex-design.rst,
in particular the section [1] about semantics:

	"mutex_unlock() may access the mutex structure even after it has
	 internally released the lock already - so it's not safe for
	 another context to acquire the mutex and assume that the
	 mutex_unlock() context is not using the structure anymore"

So if we drop our ep ref before the mutex unlock, but we weren't the
last one, we may then unlock the mutex, another user comes in, drops
_their_ reference and releases the 'ep' as it now has no users - all
while the mutex_unlock() is still accessing it.

Fix this by simply moving the ep refcount dropping to outside the mutex:
the refcount itself is atomic, and doesn't need mutex protection (that's
the whole _point_ of refcounts: unlike mutexes, they are inherently
about object lifetimes).

## References
- https://git.kernel.org/stable/c/521e9ff0b67c66a17d6f9593dfccafaa984aae4c
- https://git.kernel.org/stable/c/605c18698ecfa99165f36b7f59d3ed503e169814
- https://git.kernel.org/stable/c/6dee745bd0aec9d399df674256e7b1ecdb615444
- https://git.kernel.org/stable/c/8c2e52ebbe885c7eeaabd3b7ddcdc1246fc400d2
- https://git.kernel.org/stable/c/b0821ec902d39062356cb644c16e17a705d1c9f5
- https://project-zero.issues.chromium.org/issues/430541637
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38349.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38349
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
