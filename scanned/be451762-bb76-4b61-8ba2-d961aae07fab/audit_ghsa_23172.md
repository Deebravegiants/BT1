# [H] slixmpp Incorrect Access Control

## Summary
Severity: High
Advisory: GHSA-4g62-mfwx-4q48
CVE: CVE-2019-1000021
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4g62-mfwx-4q48
Type: github-advisory

## Affected
- PyPI: `slixmpp` — affected >=0 <1.4.2

## Details
slixmpp version before commit 7cd73b594e8122dddf847953fcfc85ab4d316416 contains an incorrect Access Control vulnerability in XEP-0223 plugin (Persistent Storage of Private Data via PubSub) options profile, used for the configuration of default access model that can result in all of the contacts of the victim can see private data having been published to a PEP node. This attack appears to be exploitable if the user of this library publishes any private data on PEP, the node isn't configured to be private. This vulnerability appears to have been fixed in commit 7cd73b594e8122dddf847953fcfc85ab4d316416 which is included in slixmpp 1.4.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1000021
- https://github.com/poezio/slixmpp/commit/7cd73b594e8122dddf847953fcfc85ab4d316416
- https://github.com/poezio/slixmpp
- https://github.com/pypa/advisory-database/tree/main/vulns/slixmpp/PYSEC-2019-121.yaml
- https://lab.louiz.org/poezio/slixmpp/commit/7cd73b594e8122dddf847953fcfc85ab4d316416
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GKBXN7EAAR7ENEZUBKV6C6MP6QBXYTWT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WIBP4LD2V4TBJSLZXDUAGQMD6CUI2TZR
- https://xmpp.org/extensions/xep-0223.html#howitworks
