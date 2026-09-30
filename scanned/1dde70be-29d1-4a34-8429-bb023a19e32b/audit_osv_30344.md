# [M] CVE-2024-51210

## Summary
Severity: Medium
Advisory: CVE-2024-51210
Aliases: GHSA-4fh7-m2wx-6wfm
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-51210
Type: osv

## Details
Firepad through 1.5.11 allows remote attackers, who have knowledge of a pad ID, to retrieve both the current text of a document and all content that has previously been pasted into the document. NOTE: in several similar products, this is the intentional behavior for anyone who knows the full document ID and corresponding URL. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://github.com/FirebaseExtended/firepad/releases/tag/v1.5.11
- https://medium.com/@adityaahuja.work/accessing-full-history-of-firepad-users-ddc889e73936
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51210.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-51210
- https://firebase.blog/posts/2013/04/announcing-firepad-our-open-source/
