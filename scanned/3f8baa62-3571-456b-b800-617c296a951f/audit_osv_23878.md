# [M] perf/core: Fix data race between perf_event_set_output() and perf_mmap_close()

## Summary
Severity: Medium
Advisory: CVE-2022-49607
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49607
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <4.9.325, >=4.10.0 <4.14.290, >=4.15.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/core: Fix data race between perf_event_set_output() and perf_mmap_close()

Yang Jihing reported a race between perf_event_set_output() and
perf_mmap_close():

	CPU1					CPU2

	perf_mmap_close(e2)
	  if (atomic_dec_and_test(&e2->rb->mmap_count)) // 1 - > 0
	    detach_rest = true

						ioctl(e1, IOC_SET_OUTPUT, e2)
						  perf_event_set_output(e1, e2)

	  ...
	  list_for_each_entry_rcu(e, &e2->rb->event_list, rb_entry)
	    ring_buffer_attach(e, NULL);
	    // e1 isn't yet added and
	    // therefore not detached

						    ring_buffer_attach(e1, e2->rb)
						      list_add_rcu(&e1->rb_entry,
								   &e2->rb->event_list)

After this; e1 is attached to an unmapped rb and a subsequent
perf_mmap() will loop forever more:

	again:
		mutex_lock(&e->mmap_mutex);
		if (event->rb) {
			...
			if (!atomic_inc_not_zero(&e->rb->mmap_count)) {
				...
				mutex_unlock(&e->mmap_mutex);
				goto again;
			}
		}

The loop in perf_mmap_close() holds e2->mmap_mutex, while the attach
in perf_event_set_output() holds e1->mmap_mutex. As such there is no
serialization to avoid this race.

Change perf_event_set_output() to take both e1->mmap_mutex and
e2->mmap_mutex to alleviate that problem. Additionally, have the loop
in perf_mmap() detach the rb directly, this avoids having to wait for
the concurrent perf_mmap_close() to get around to doing it to make
progress.

## References
- https://git.kernel.org/stable/c/17f5417194136517ee9bbd6511249e5310e5617c
- https://git.kernel.org/stable/c/3bbd868099287ff9027db59029b502fcfa2202a0
- https://git.kernel.org/stable/c/43128b3eee337824158f34da6648163d2f2fb937
- https://git.kernel.org/stable/c/68e3c69803dada336893640110cb87221bb01dcf
- https://git.kernel.org/stable/c/98c3c8fd0d4c560e0f8335b79c407bbf7fc9462c
- https://git.kernel.org/stable/c/a9391ff7a7c5f113d6f2bf6621d49110950de49c
- https://git.kernel.org/stable/c/da3c256e2d0ebc87c7db0c605c9692b6f1722074
- https://git.kernel.org/stable/c/f836f9ac95df15f1e0af4beb0ec20021e8c91998
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49607.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49607
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
