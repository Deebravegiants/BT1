# [H] CVE-2020-36079

## Summary
Severity: High
Advisory: CVE-2020-36079
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2020-36079
Type: osv

## Details
Zenphoto through 1.5.7 is affected by authenticated arbitrary file upload, leading to remote code execution. The attacker must navigate to the uploader plugin, check the elFinder box, and then drag and drop files into the Files(elFinder) portion of the UI. This can, for example, place a .php file in the server's uploaded/ directory. NOTE: the vendor disputes this because exploitation can only be performed by an admin who has "lots of other possibilities to harm a site.

## References
- https://github.com/zenphoto/zenphoto/issues/1292
- https://www.zenphoto.org/news/why-not-every-security-issue-is-really-an-issue/
- http://packetstormsecurity.com/files/161569/Zenphoto-CMS-1.5.7-Shell-Upload.html
