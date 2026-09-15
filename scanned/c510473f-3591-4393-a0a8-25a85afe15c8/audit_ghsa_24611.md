# [C] Openstack Magnum Unsafe Credential Handling

## Summary
Severity: Critical
Advisory: GHSA-793v-r35j-9rp9
CVE: CVE-2016-7404
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-793v-r35j-9rp9
Type: github-advisory

## Affected
- PyPI: `openstack-magnum` — affected >=0 <5.0.0

## Details
OpenStack Magnum passes OpenStack credentials into the Heat templates creating its instances. While these should just be used for retrieving the instances' SSL certificates, they allow full API access, though and can be used to perform any API operation the user is authorized to perform.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7404
- https://github.com/openstack/magnum/commit/e93d82e8b3bc19211efd54edc17aebdca50670c1
- https://bugs.launchpad.net/magnum/+bug/1620536
- https://bugzilla.suse.com/show_bug.cgi?id=998182
- https://github.com/openstack/magnum
- https://opendev.org/openstack/magnum/commit/0bb0d6486d6771ee21bbf897a091b1aa59e01b22
- https://web.archive.org/web/20210124052053/https://www.securityfocus.com/bid/98467
