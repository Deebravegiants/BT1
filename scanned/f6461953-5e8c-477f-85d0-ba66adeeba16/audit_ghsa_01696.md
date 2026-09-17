# [H] Insufficient output escaping of attachment names in PHPMailer

## Summary
Severity: High
Advisory: GHSA-f7hx-fqxw-rvvj
CVE: CVE-2020-13625
CWE: CWE-116
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-05-27
Source: https://github.com/advisories/GHSA-f7hx-fqxw-rvvj
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=0 <6.1.6

## Details
### Impact
CWE-116: Incorrect output escaping.

An attachment added like this (note the double quote within the attachment name, which is entirely valid):

    $mail->addAttachment('/tmp/attachment.tmp', 'filename.html";.jpg');

Will result in a message containing these headers:

    Content-Type: application/octet-stream; name="filename.html";.jpg"
    Content-Disposition: attachment; filename="filename.html";.jpg"

The attachment will be named `filename.html`, and the trailing `";.jpg"` will be ignored. Mail filters that reject `.html` attachments but permit `.jpg` attachments may be fooled by this.

Note that the MIME type itself is obtained automatically from the *source filename* (in this case `attachment.tmp`, which maps to a generic `application/octet-stream` type), and not the *name* given to the attachment (though these are the same if a separate name is not provided), though it can be set explicitly in other parameters to attachment methods.

### Patches
Patched in PHPMailer 6.1.6 by escaping double quotes within the name using a backslash, as per RFC822 section 3.4.1, resulting in correctly escaped headers like this:

    Content-Type: application/octet-stream; name="filename.html\";.jpg"
    Content-Disposition: attachment; filename="filename.html\";.jpg"

### Workarounds
Reject or filter names and filenames containing double quote (`"`) characters before passing them to attachment functions such as `addAttachment()`.

### References
[CVE-2020-13625](https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2020-13625).
[PHPMailer 6.1.6 release](https://github.com/PHPMailer/PHPMailer/releases/tag/v6.1.6)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the PHPMailer repo](https://github.com/PHPMailer/PHPMailer/issues)

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-f7hx-fqxw-rvvj
- https://nvd.nist.gov/vuln/detail/CVE-2020-13625
- https://github.com/PHPMailer/PHPMailer/commit/c2796cb1cb99d7717290b48c4e6f32cb6c60b7b3
- https://github.com/PHPMailer/PHPMailer
- https://github.com/PHPMailer/PHPMailer/releases/tag/v6.1.6
- https://lists.debian.org/debian-lts-announce/2020/06/msg00014.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00004.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EFM3BZABL6RUHTVMXSC7OFMP4CKWMRPJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SMH4TC5XTS3KZVGMSKEPPBZ2XTZCKKCX
- https://usn.ubuntu.com/4505-1
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00067.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00085.html
