# [H] CVE-2019-9858

## Summary
Severity: High
Advisory: CVE-2019-9858
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-29
Source: https://osv.dev/vulnerability/CVE-2019-9858
Type: osv

## Details
Remote code execution was discovered in Horde Groupware Webmail 5.2.22 and 5.2.17. Horde/Form/Type.php contains a vulnerable class that handles image upload in forms. When the Horde_Form_Type_image method onSubmit() is called on uploads, it invokes the functions getImage() and _getUpload(), which uses unsanitized user input as a path to save the image. The unsanitized POST parameter object[photo][img][file] is saved in the $upload[img][file] PHP variable, allowing an attacker to manipulate the $tmp_file passed to move_uploaded_file() to save the uploaded file. By setting the parameter to (for example) ../usr/share/horde/static/bd.php, one can write a PHP backdoor inside the web root. The static/ destination folder is a good candidate to drop the backdoor because it is always writable in Horde installations. (The unsanitized POST parameter went probably unnoticed because it's never submitted by the forms, which default to securely using a random path.)

## References
- https://lists.debian.org/debian-lts-announce/2019/06/msg00007.html
- https://seclists.org/bugtraq/2019/Jun/31
- https://www.debian.org/security/2019/dsa-4468
- http://packetstormsecurity.com/files/152476/Horde-Form-Shell-Upload.html
- https://ssd-disclosure.com/?p=3814&preview=true
