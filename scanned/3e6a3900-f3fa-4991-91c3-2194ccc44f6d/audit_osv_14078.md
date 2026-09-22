# [C] CVE-2018-6948

## Summary
Severity: Critical
Advisory: CVE-2018-6948
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2018-6948
Type: osv

## Details
In CCN-lite 2, the function ccnl_prefix_to_str_detailed can cause a buffer overflow, when writing a prefix to the buffer buf. The maximal size of the prefix is CCNL_MAX_PREFIX_SIZE; the buffer has the size CCNL_MAX_PREFIX_SIZE. However, when NFN is enabled, additional characters are written to the buffer (e.g., the "NFN" and "R2C" tags). Therefore, sending an NFN-R2C packet with a prefix of size CCNL_MAX_PREFIX_SIZE can cause an overflow of buf inside ccnl_prefix_to_str_detailed.

## References
- https://github.com/cn-uofbasel/ccn-lite/issues/193
