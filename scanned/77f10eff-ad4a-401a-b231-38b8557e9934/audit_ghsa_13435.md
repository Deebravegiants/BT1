# [M] Indico vulnerable to Cross-Site-Scripting via confirmation prompts

## Summary
Severity: Medium
Advisory: GHSA-fmqq-25x9-c6hm
CVE: CVE-2023-37901
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-21
Source: https://github.com/advisories/GHSA-fmqq-25x9-c6hm
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <3.2.6

## Details
### Impact
There is a Cross-Site-Scripting vulnerability in confirmation prompts commonly used when deleting content from Indico.
Exploitation requires someone with at least submission privileges (such as a speaker) and then someone else to attempt to delete this content.

Considering that event organizers may want to delete suspicious-looking content when spotting it, there is a non-negligible risk of such an attack to succeed. The risk of this could be further increased when combined with some some social engineering pointing the victim towards this content.

### Patches
You need to update to [Indico 3.2.6](https://github.com/indico/indico/releases/tag/v3.2.6) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

### Workarounds
Only let trustworthy users manage categories, create events or upload materials ("submission" privileges on a contribution/event). This should already be the case in a properly-configured setup when it comes to category/event management.

Note that a conference doing a Call for Abstracts actively invites external speakers (who the organizers may not know and thus cannot fully trust) to submit content, hence the need to update to a a fixed version ASAP in particular when using such workflows.

For more information

If you have any questions or comments about this advisory:

* Open a thread in [our forum](https://talk.getindico.io/)
* Email us privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-fmqq-25x9-c6hm
- https://nvd.nist.gov/vuln/detail/CVE-2023-37901
- https://github.com/indico/indico/commit/2ee636d318653fb1ab193803dafbfe3e371d4130
- https://docs.getindico.io/en/stable/installation/upgrade
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.2.6
- https://github.com/pypa/advisory-database/tree/main/vulns/indico/PYSEC-2023-129.yaml
