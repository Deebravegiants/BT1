# [M] block/rnbd-srv: Check for unlikely string overflow

## Summary
Severity: Medium
Advisory: CVE-2023-52618
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2023-52618
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

block/rnbd-srv: Check for unlikely string overflow

Since "dev_search_path" can technically be as large as PATH_MAX,
there was a risk of truncation when copying it and a second string
into "full_path" since it was also PATH_MAX sized. The W=1 builds were
reporting this warning:

drivers/block/rnbd/rnbd-srv.c: In function 'process_msg_open.isra':
drivers/block/rnbd/rnbd-srv.c:616:51: warning: '%s' directive output may be truncated writing up to 254 bytes into a region of size between 0 and 4095 [-Wformat-truncation=]
  616 |                 snprintf(full_path, PATH_MAX, "%s/%s",
      |                                                   ^~
In function 'rnbd_srv_get_full_path',
    inlined from 'process_msg_open.isra' at drivers/block/rnbd/rnbd-srv.c:721:14: drivers/block/rnbd/rnbd-srv.c:616:17: note: 'snprintf' output between 2 and 4351 bytes into a destination of size 4096
  616 |                 snprintf(full_path, PATH_MAX, "%s/%s",
      |                 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  617 |                          dev_search_path, dev_name);
      |                          ~~~~~~~~~~~~~~~~~~~~~~~~~~

To fix this, unconditionally check for truncation (as was already done
for the case where "%SESSNAME%" was present).

## References
- https://git.kernel.org/stable/c/5b9ea86e662035a886ccb5c76d56793cba618827
- https://git.kernel.org/stable/c/95bc866c11974d3e4a9d922275ea8127ff809cf7
- https://git.kernel.org/stable/c/9e4bf6a08d1e127bcc4bd72557f2dfafc6bc7f41
- https://git.kernel.org/stable/c/a2c6206f18104fba7f887bf4dbbfe4c41adc4339
- https://git.kernel.org/stable/c/af7bbdac89739e2e7380387fda598848d3b7010f
- https://git.kernel.org/stable/c/f6abd5e17da33eba15df2bddc93413e76c2b55f7
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52618.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52618
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
