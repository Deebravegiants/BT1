# [H] CVE-2025-45767

## Summary
Severity: High
Advisory: CVE-2025-45767
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-08-01
Source: https://osv.dev/vulnerability/CVE-2025-45767
Type: osv

## Details
jose v6.0.10 was discovered to contain weak encryption. NOTE: this is disputed by a third party because the claim of "do not meet recommended security standards" does not reflect guidance in a final publication.

## References
- https://github.com/panva/jose/discussions/813
- https://gist.github.com/ZupeiNie/705a606fbb99f3bb8c9b51e5bc13c91d
- https://gist.github.com/ZupeiNie/705a606fbb99f3bb8c9b51e5bc13c91d?permalink_comment_id=5711572#gistcomment-5711572
- https://github.com/panva
- https://github.com/panva/jose/blob/1e36dd29e76511e06737e5d5d500d81e01a9c3d2/src/lib/check_key_length.ts#L6-L7
- https://github.com/panva/jose
