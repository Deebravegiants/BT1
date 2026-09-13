# [H] CVE-2020-13443

## Summary
Severity: High
Advisory: CVE-2020-13443
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-24
Source: https://osv.dev/vulnerability/CVE-2020-13443
Type: osv

## Details
ExpressionEngine before 5.3.2 allows remote attackers to upload and execute arbitrary code in a .php%20 file via Compose Msg, Add attachment, and Save As Draft actions. A user with low privileges (member) is able to upload this. It is possible to bypass the MIME type check and file-extension check while uploading new files. Short aliases are not used for an attachment; instead, direct access is allowed to the uploaded files. It is possible to upload PHP only if one has member access, or registration/forum is enabled and one can create a member with the default group id of 5. To exploit this, one must to be able to send and compose messages (at least).

## References
- https://expressionengine.com/blog
- https://gist.github.com/mariuszpoplwski/51604d8a6d7d78fffdf590c25e844e09
