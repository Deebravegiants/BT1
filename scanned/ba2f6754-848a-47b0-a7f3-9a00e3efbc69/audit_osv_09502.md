# [M] CVE-2017-0896

## Summary
Severity: Medium
Advisory: CVE-2017-0896
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-0896
Type: osv

## Details
Zulip Server 1.5.1 and below suffer from an error in the implementation of the invite_by_admins_only setting in the Zulip group chat application server that allowed an authenticated user to invite other users to join a Zulip organization even if the organization was configured to prevent this.

## References
- https://groups.google.com/forum/#%21msg/zulip-announce/sUYeJv-fFmg/2TU2TLmNAwAJ
- https://hackerone.com/reports/224210
- https://github.com/zulip/zulip/commit/1f48fa27672170bba3b9a97384905bb04c18761b
