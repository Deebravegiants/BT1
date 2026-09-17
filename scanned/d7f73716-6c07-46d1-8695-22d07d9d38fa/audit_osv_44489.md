# [M] Ash.Vector wraps the 16-bit dimension header for vectors over 65,535 elements, corrupting data and crashing reads

## Summary
Severity: Medium
Advisory: CVE-2026-82737
Aliases: EEF-CVE-2026-82737, GHSA-68q3-w4w3-2gfv
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82737
Type: osv

## Details
Integer Overflow or Wraparound vulnerability in ash-project ash lets an attacker corrupt a stored vector and crash later reads of it by submitting a vector with more than 65,535 elements.

Ash.Vector.new/1 (lib/ash/vector.ex) encodes a vector as <<dim::unsigned-16, 0::unsigned-16>> followed by the element floats, packing the element count into a 16-bit field without checking its range. A list of more than 65,535 elements wraps the dimension modulo 65,536, so the encoded header records a dimension that disagrees with the number of stored floats. from_binary/1 later reads binary-size(dim)-unit(32) from the wrapped header, so every read of the corrupted value misparses and raises, denying access to the affected record. The fix rejects any vector whose dimension exceeds 65,535.

This issue affects ash: from 2.14.13 before 3.32.2.

## References
- https://cna.erlef.org/cves/CVE-2026-82737.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82737
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82737.json
- https://github.com/ash-project/ash/security/advisories/GHSA-68q3-w4w3-2gfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-82737
- https://github.com/ash-project/ash/commit/cef5eb7b0693f04d1699a36e02a4e09ce1e7bffe
- https://github.com/ash-project/ash
