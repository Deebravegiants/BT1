# [H] CVE-2022-37603

## Summary
Severity: High
Advisory: CVE-2022-37603
Aliases: GHSA-3rfm-jhwj-7488
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/CVE-2022-37603
Type: osv

## Details
A Regular expression denial of service (ReDoS) flaw was found in Function interpolateName in interpolateName.js in webpack loader-utils 2.0.0 via the url variable in interpolateName.js.

## References
- https://github.com/webpack/loader-utils/blob/d9f4e23cf411d8556f8bac2d3bf05a6e0103b568/lib/interpolateName.js#L107
- https://github.com/webpack/loader-utils/blob/d9f4e23cf411d8556f8bac2d3bf05a6e0103b568/lib/interpolateName.js#L38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37603.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ERN6YE3DS7NBW7UH44SCJBMNC2NWQ7SM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KAC5KQ2SEWAMQ6UZAUBZ5KXKEOESH375/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VNV2GNZXOTEDAJRFH3ZYWRUBGIVL7BSU/
- https://nvd.nist.gov/vuln/detail/CVE-2022-37603
- https://github.com/webpack/loader-utils/issues/213
