# [H] CVE-2020-11807

## Summary
Severity: High
Advisory: CVE-2020-11807
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-11807
Type: osv

## Details
Because of Unrestricted Upload of a File with a Dangerous Type, Sourcefabric Newscoop 4.4.7 allows an authenticated user to execute arbitrary PHP code (and sometimes terminal commands) on a server by making an avatar update and then visiting the avatar file under the /images/ path.

## References
- https://github.com/sourcefabric/Newscoop/blob/3df835637609a5a42530b2a4611177c634ad6274/newscoop/library/Newscoop/Image/ImageService.php#L226
- https://gist.github.com/V-Rico/82e9e52ac451dc20eef87b0999b3b1ee
