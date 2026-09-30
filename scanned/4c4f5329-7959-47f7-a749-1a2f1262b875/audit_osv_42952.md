# [C] ntfs: fix off-by-one in mapping pairs decoding bounds checks

## Summary
Severity: Critical
Advisory: CVE-2026-72210
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72210
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: fix off-by-one in mapping pairs decoding bounds checks

In ntfs_mapping_pairs_decompress(), attr_end points one byte past the
end of the attribute record:

    attr_end = (u8 *)attr + le32_to_cpu(attr->length);

The two bounds checks validating that mapping pair data bytes fit within
the attribute use strict greater-than (>), which allows a one-byte
out-of-bounds read when the data extends exactly to attr_end:

  b = *buf & 0xf;
  if (b) {
      if (unlikely(buf + b > attr_end))   // off-by-one
          goto io_error;
      for (deltaxcn = (s8)buf[b--]; b; b--)
          deltaxcn = (deltaxcn << 8) + buf[b];
  }

When buf + b == attr_end, the check evaluates to false and buf[b] reads
one byte past the valid attribute boundary. The same pattern appears in
the LCN delta bytes check.

Fix both checks to use >= so that buf[b] at exactly attr_end is
correctly rejected as out of bounds.

## References
- https://git.kernel.org/stable/c/18760a74ef7c28df93726445b5595162e62ed341
- https://git.kernel.org/stable/c/bfe835e535fe0aa5767fdd8116f62e835ba50b55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72210.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72210
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
