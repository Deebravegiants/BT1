# [H] wifi: carl9170: re-fix fortified-memset warning

## Summary
Severity: High
Advisory: CVE-2024-38616
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38616
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: carl9170: re-fix fortified-memset warning

The carl9170_tx_release() function sometimes triggers a fortified-memset
warning in my randconfig builds:

In file included from include/linux/string.h:254,
                 from drivers/net/wireless/ath/carl9170/tx.c:40:
In function 'fortify_memset_chk',
    inlined from 'carl9170_tx_release' at drivers/net/wireless/ath/carl9170/tx.c:283:2,
    inlined from 'kref_put' at include/linux/kref.h:65:3,
    inlined from 'carl9170_tx_put_skb' at drivers/net/wireless/ath/carl9170/tx.c:342:9:
include/linux/fortify-string.h:493:25: error: call to '__write_overflow_field' declared with attribute warning: detected write beyond size of field (1st parameter); maybe use struct_group()? [-Werror=attribute-warning]
  493 |                         __write_overflow_field(p_size_field, size);

Kees previously tried to avoid this by using memset_after(), but it seems
this does not fully address the problem. I noticed that the memset_after()
here is done on a different part of the union (status) than the original
cast was from (rate_driver_data), which may confuse the compiler.

Unfortunately, the memset_after() trick does not work on driver_rates[]
because that is part of an anonymous struct, and I could not get
struct_group() to do this either. Using two separate memset() calls
on the two members does address the warning though.

## References
- https://git.kernel.org/stable/c/042a39bb8e0812466327a5102606e88a5a4f8c02
- https://git.kernel.org/stable/c/066afafc10c9476ee36c47c9062527a17e763901
- https://git.kernel.org/stable/c/0c38c9c460bb8ce8d6f6cf316e0d71a70983ec83
- https://git.kernel.org/stable/c/13857683126e8a6492af73c74d702835f7a2175b
- https://git.kernel.org/stable/c/87586467098281f04fa93e59fe3a516b954bddc4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38616.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38616
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
