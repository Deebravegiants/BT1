# [C] net: tls: handle backlogging of crypto requests

## Summary
Severity: Critical
Advisory: CVE-2024-26584
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-26584
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.15.160, >=5.16.0 <6.1.84, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tls: handle backlogging of crypto requests

Since we're setting the CRYPTO_TFM_REQ_MAY_BACKLOG flag on our
requests to the crypto API, crypto_aead_{encrypt,decrypt} can return
 -EBUSY instead of -EINPROGRESS in valid situations. For example, when
the cryptd queue for AESNI is full (easy to trigger with an
artificially low cryptd.cryptd_max_cpu_qlen), requests will be enqueued
to the backlog but still processed. In that case, the async callback
will also be called twice: first with err == -EINPROGRESS, which it
seems we can just ignore, then with err == 0.

Compared to Sabrina's original patch this version uses the new
tls_*crypt_async_wait() helpers and converts the EBUSY to
EINPROGRESS to avoid having to modify all the error handling
paths. The handling is identical.

## References
- https://git.kernel.org/stable/c/13eca403876bbea3716e82cdfe6f1e6febb38754
- https://git.kernel.org/stable/c/3ade391adc584f17b5570fd205de3ad029090368
- https://git.kernel.org/stable/c/8590541473188741055d27b955db0777569438e3
- https://git.kernel.org/stable/c/ab6397f072e5097f267abf5cb08a8004e6b17694
- https://git.kernel.org/stable/c/cd1bbca03f3c1d845ce274c0d0a66de8e5929f72
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EZOU3745CWCDZ7EMKMXB2OEEIB5Q3IWM/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26584.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26584
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
