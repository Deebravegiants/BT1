# [M] md/raid5-cache: fix null-ptr-deref for r5l_flush_stripe_to_raid()

## Summary
Severity: Medium
Advisory: CVE-2023-53210
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53210
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid5-cache: fix null-ptr-deref for r5l_flush_stripe_to_raid()

r5l_flush_stripe_to_raid() will check if the list 'flushing_ios' is
empty, and then submit 'flush_bio', however, r5l_log_flush_endio()
is clearing the list first and then clear the bio, which will cause
null-ptr-deref:

T1: submit flush io
raid5d
 handle_active_stripes
  r5l_flush_stripe_to_raid
   // list is empty
   // add 'io_end_ios' to the list
   bio_init
   submit_bio
   // io1

T2: io1 is done
r5l_log_flush_endio
 list_splice_tail_init
 // clear the list
			T3: submit new flush io
			...
			r5l_flush_stripe_to_raid
			 // list is empty
			 // add 'io_end_ios' to the list
			 bio_init
 bio_uninit
 // clear bio->bi_blkg
			 submit_bio
			 // null-ptr-deref

Fix this problem by clearing bio before clearing the list in
r5l_log_flush_endio().

## References
- https://git.kernel.org/stable/c/0d0bd28c500173bfca78aa840f8f36d261ef1765
- https://git.kernel.org/stable/c/711fb92606208a8626b785da4f9f23d648a5b6c8
- https://git.kernel.org/stable/c/7a8b6d93991bf4b72b3f959baea35397c6c8e521
- https://git.kernel.org/stable/c/e46b2e7be8059d156af8c011dd8d665229b65886
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53210.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53210
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
