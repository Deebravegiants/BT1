# [H] Denial of service in XStream

## Summary
Severity: High
Advisory: GHSA-7hwc-46rm-65jh
CVE: CVE-2017-7957
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-06-30
Source: https://github.com/advisories/GHSA-7hwc-46rm-65jh
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.10

## Details
XStream through 1.4.9, when a certain denyTypes workaround is not used, mishandles attempts to create an instance of the primitive type 'void' during unmarshalling, leading to a remote application crash, as demonstrated by an xstream.fromXML("<void/>") call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7957
- https://github.com/x-stream/xstream/commit/6e546ec366419158b1e393211be6d78ab9604ab
- https://github.com/x-stream/xstream/commit/8542d02d9ac5d384c85f4b33d6c1888c53bd55d
- https://github.com/x-stream/xstream/commit/b3570be2f39234e61f99f9a20640756ea71b1b4
- https://access.redhat.com/errata/RHSA-2017:1832
- https://access.redhat.com/errata/RHSA-2017:2888
- https://access.redhat.com/errata/RHSA-2017:2889
- https://exchange.xforce.ibmcloud.com/vulnerabilities/125800
- https://github.com/x-stream/xstream
- https://www-prd-trops.events.ibm.com/node/715749
- http://www.debian.org/security/2017/dsa-3841
- http://www.securityfocus.com/bid/100687
- http://www.securitytracker.com/id/1039499
- http://x-stream.github.io/CVE-2017-7957.html
