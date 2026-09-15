# [C] netfilter: nf_conntrack_sip: don't use simple_strtoul

## Summary
Severity: Critical
Advisory: CVE-2026-52986
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52986
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_sip: don't use simple_strtoul

Replace unsafe port parsing in epaddr_len(), ct_sip_parse_header_uri(),
and ct_sip_parse_request() with a new sip_parse_port() helper that
validates each digit against the buffer limit, eliminating the use of
simple_strtoul() which assumes NUL-terminated strings.

The previous code dereferenced pointers without bounds checks after
sip_parse_addr() and relied on simple_strtoul() on non-NUL-terminated
skb data. A port that reaches the buffer limit without a trailing
character is also rejected as malformed.

Also get rid of all simple_strtoul() usage in conntrack, prefer a
stricter version instead.  There are intentional changes:

- Bail out if number is > UINT_MAX and indicate a failure, same for
  too long sequences.
  While we do accept 05535 as port 5535, we will not accept e.g.
  'sip:10.0.0.1:005060'.  While its syntactically valid under RFC 3261,
  we should restrict this to not waste cycles when presented with
  malformed packets with 64k '0' characters.

- Force base 10 in ct_sip_parse_numerical_param(). This is used to fetch
  'expire=' and 'rports='; both are expected to use base-10.

- In nf_nat_sip.c, only accept the parsed value if its within the 1k-64k
  range.

- epaddr_len now returns 0 if the port is invalid, as it already does
  for invalid ip addresses.  This is intentional. nf_conntrack_sip
  performs lots of guesswork to find the right parts of the message
  to parse.  Being stricter could break existing setups.
  Connection tracking helpers are designed to allow traffic to
  pass, not to block it.

Based on an earlier patch from Jenny Guanni Qu <qguanni@gmail.com>.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/523762e3b6933fff81f01dfa3c60c0774044cdab
- https://git.kernel.org/stable/c/7df9863bf538a626e8a684e59cb2c43eac0ef3c8
- https://git.kernel.org/stable/c/8cd0358379570003659186706e077929d6930c40
- https://git.kernel.org/stable/c/8cf6809cddcbe301aedfc6b51bcd4944d45795f6
- https://git.kernel.org/stable/c/9c6afcb1c3cbb2c0da65b8515ac14d7273872f84
- https://git.kernel.org/stable/c/9f69c323ae0ab517e595c2cc74e0ae0d9d085611
- https://git.kernel.org/stable/c/b3264c977e79d8a25778d4fd11520f00fea1329c
- https://git.kernel.org/stable/c/ea2ecd29b8f4433e52607192ca91084f95787ca0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52986.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52986
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
