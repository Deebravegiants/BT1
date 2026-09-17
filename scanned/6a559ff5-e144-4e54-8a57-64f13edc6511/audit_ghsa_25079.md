# [C] OpenStack Octavia Amphora-Agent not requiring Client-Certificate

## Summary
Severity: Critical
Advisory: GHSA-r4v4-3jj7-jc29
CVE: CVE-2019-17134
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r4v4-3jj7-jc29
Type: github-advisory

## Affected
- PyPI: `octavia` — affected >=0.10.0 <2.1.2
- PyPI: `octavia` — affected >=3.0.0 <3.2.0
- PyPI: `octavia` — affected >=4.0.0 <4.1.0

## Details
Amphora Images in OpenStack Octavia >=0.10.0 <2.1.2, >=3.0.0 <3.2.0, >=4.0.0 <4.1.0 allows anyone with access to the management network to bypass client-certificate based authentication and retrieve information or issue configuration commands via simple HTTP requests to the Agent on port https/9443, because the `cmd/agent.py` gunicorn cert_reqs option is True but is supposed to be ssl.CERT_REQUIRED.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17134
- https://github.com/openstack/octavia/commit/1725517d1d209f26b2275306d83e49c099dcbe1a
- https://github.com/openstack/octavia/commit/2976a7f0f109e17930db8a61136526ead44ea7e5
- https://github.com/openstack/octavia/commit/624ff08f27bcb73788663cbe6d35cbe29c537844
- https://github.com/openstack/octavia/commit/89a2f6e0136ad49d928eb65b4cf555af2a2b8ab1
- https://github.com/openstack/octavia/commit/b0c2cd7b4c835c391cfedf12cf9f9ff8a0aabd17
- https://github.com/openstack/octavia/commit/c2fdffc3b748f8007c72e52df257e38756923b40
- https://github.com/openstack/octavia
- https://review.opendev.org/686541
- https://review.opendev.org/686543
- https://review.opendev.org/686544
- https://review.opendev.org/686545
- https://review.opendev.org/686546
- https://review.opendev.org/686547
- https://security.openstack.org/ossa/OSSA-2019-005.html
- https://storyboard.openstack.org/#!/story/2006660
