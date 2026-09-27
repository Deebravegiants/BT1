# [M] CVE-2018-25103

## Summary
Severity: Medium
Advisory: CVE-2018-25103
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-06-17
Source: https://osv.dev/vulnerability/CVE-2018-25103
Type: osv

## Details
There exists use-after-free vulnerabilities in lighttpd <= 1.4.50 request parsing which might read from invalid pointers to memory used in the same request, not from other requests.

## References
- https://9443417.fs1.hubspotusercontent-na1.net/hubfs/9443417/Security%20Advisories/2024/AMI-SA-2024002.pdf
- https://www.kb.cert.org/vuls/id/312260
- https://github.com/lighttpd/lighttpd1.4/commit/d161f53de04bc826ce1bdaeb3dce2c72ca50a3f8
- https://github.com/lighttpd/lighttpd1.4/commit/df8e4f95614e476276a55e34da2aa8b00b1148e9
- https://blogvdoo.wordpress.com/2018/11/06/giving-back-securing-open-source-iot-projects/#more-736
- https://www.runzero.com/blog/lighttpd/
