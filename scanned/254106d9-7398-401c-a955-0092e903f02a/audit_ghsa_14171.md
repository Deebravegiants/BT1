# [C] Buffer overflow in sponge queue functions

## Summary
Severity: Critical
Advisory: GHSA-6w4m-2xhg-2658
CVE: CVE-2022-37454
CWE: CWE-190
Ecosystem: PyPI, RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-6w4m-2xhg-2658
Type: github-advisory

## Affected
- PyPI: `pysha3` — affected >=0
- RubyGems: `sha3` — affected >=0 <1.0.5

## Details
### Impact

The Keccak sponge function interface accepts partial inputs to be absorbed and partial outputs to be squeezed. A buffer can overflow when partial data with some specific sizes are queued, where at least one of them has a length of 2^32 - 200 bytes or more.

### Patches

Yes, see commit [fdc6fef0](https://github.com/XKCP/XKCP/commit/fdc6fef075f4e81d6b1bc38364248975e08e340a).

### Workarounds

The problem can be avoided by limiting the size of the partial input data (or partial output digest) below 2^32 - 200 bytes. Multiple calls to the queue system can be chained at a higher level to retain the original functionality. Alternatively, one can process the entire input (or produce the entire output) at once, avoiding the queuing functions altogether.

### References

See [issue #105](https://github.com/XKCP/XKCP/issues/105) for more details.

## References
- https://github.com/XKCP/XKCP/security/advisories/GHSA-6w4m-2xhg-2658
- https://nvd.nist.gov/vuln/detail/CVE-2022-37454
- https://github.com/XKCP/XKCP/issues/105
- https://github.com/johanns/sha3/issues/17
- https://github.com/tiran/pysha3/issues/29
- https://github.com/XKCP/XKCP/commit/fdc6fef075f4e81d6b1bc38364248975e08e340a
- https://github.com/johanns/sha3/commit/5f2e8118a62831911703c8753ff2435c3b5d7312
- https://www.debian.org/security/2022/dsa-5269
- https://www.debian.org/security/2022/dsa-5267
- https://security.gentoo.org/glsa/202305-02
- https://news.ycombinator.com/item?id=35050307
- https://news.ycombinator.com/item?id=33281106
- https://mouha.be/sha-3-buffer-overflow
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CMIEXLMTW5GO36HTFFWIPB3OHZXCT3G4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3ALQ6BDDPX5HU5YBQOBMDVAA2TSGDKIJ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CMIEXLMTW5GO36HTFFWIPB3OHZXCT3G4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3ALQ6BDDPX5HU5YBQOBMDVAA2TSGDKIJ
- https://lists.debian.org/debian-lts-announce/2022/11/msg00000.html
- https://lists.debian.org/debian-lts-announce/2022/10/msg00041.html
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sha3/CVE-2022-37454.yml
