# [H] esp: fix page frag reference leak on skb_to_sgvec failure

## Summary
Severity: High
Advisory: CVE-2026-63872
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63872
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

esp: fix page frag reference leak on skb_to_sgvec failure

In esp_output_tail(), when esp->inplace is false, the old skb page frags
are replaced with a new page from the xfrm page_frag cache. The source
scatterlist (sg) is built from the old frags before the replacement, and
esp_ssg_unref() is responsible for releasing the old page references
after the crypto operation completes.

However, if the second skb_to_sgvec() call (which builds the destination
scatterlist from the new page) fails, the code jumps to error_free which
only calls kfree(tmp). The old page frag references captured in the
source scatterlist are never released:

  1. sg[] is built from old frags via skb_to_sgvec() (no extra get_page)
  2. nr_frags is set to 1 and frag[0] is replaced with the new page
  3. Second skb_to_sgvec() fails -> goto error_free
  4. kfree(tmp) frees the sg[] memory but old frags are not unref'd
  5. kfree_skb() only releases frag[0] (the new page), not the old ones

Fix this by adding a bool parameter to esp_ssg_unref() that, when true,
unconditionally unrefs the source scatterlist frags without checking
req->src and req->dst, since those fields are not yet initialized by
aead_request_set_crypt() at the point of the error. Existing callers
pass false to preserve the original behavior.

The same issue exists in both esp4 and esp6 as the code is identical.

## References
- https://git.kernel.org/stable/c/2982e599fff6faa21c8df147d96fc7af6c1a2f24
- https://git.kernel.org/stable/c/e705b8ff4dd38fb8fe4e6fdc5378a86acea4feb5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63872.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
