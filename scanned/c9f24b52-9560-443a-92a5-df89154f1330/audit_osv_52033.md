# [M] CVE-2021-46988

## Summary
Severity: Medium
Advisory: CVE-2021-46988
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46988
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

userfaultfd: release page in error path to avoid BUG_ON

Consider the following sequence of events:

1. Userspace issues a UFFD ioctl, which ends up calling into
   shmem_mfill_atomic_pte(). We successfully account the blocks, we
   shmem_alloc_page(), but then the copy_from_user() fails. We return
   -ENOENT. We don't release the page we allocated.
2. Our caller detects this error code, tries the copy_from_user() after
   dropping the mmap_lock, and retries, calling back into
   shmem_mfill_atomic_pte().
3. Meanwhile, let's say another process filled up the tmpfs being used.
4. So shmem_mfill_atomic_pte() fails to account blocks this time, and
   immediately returns - without releasing the page.

This triggers a BUG_ON in our caller, which asserts that the page
should always be consumed, unless -ENOENT is returned.

To fix this, detect if we have such a "dangling" page when accounting
fails, and if so, release it before returning.

## References
- https://git.kernel.org/stable/c/140cfd9980124aecb6c03ef2e69c72d0548744de
- https://git.kernel.org/stable/c/2d59a0ed8b26b8f3638d8afc31f839e27759f1f6
- https://git.kernel.org/stable/c/319116227e52d49eee671f0aa278bac89b3c1b69
- https://git.kernel.org/stable/c/7ed9d238c7dbb1fdb63ad96a6184985151b0171c
- https://git.kernel.org/stable/c/ad53127973034c63b5348715a1043d0e80ceb330
- https://git.kernel.org/stable/c/b3f1731c6d7fbc1ebe3ed8eff6d6bec56d76ff43
- https://git.kernel.org/stable/c/07c9b834c97d0fa3402fb7f3f3b32df370a6ff1f
