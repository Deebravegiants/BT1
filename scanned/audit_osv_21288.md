# [M] CVE-2021-41714

## Summary
Severity: Medium
Advisory: CVE-2021-41714
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-05-23
Source: https://osv.dev/vulnerability/CVE-2021-41714
Type: osv

## Details
In Tipask < 3.5.9, path parameters entered by the user are not validated when downloading attachments, a registered user can download arbitrary files on the Tipask server such as .env, /etc/passwd, laravel.log, causing infomation leakage.

## References
- https://www.yuque.com/henry-weply/penetration/fza5hm
- https://github.com/sdfsky/tipask/commit/9b5f13d1708e9a5dc0959cb8a97be1c32b94ca69
- https://github.com/sdfsky/tipask/blob/c4e6aa9f6017c9664780570016954c0922d203b7/app/Http/Controllers/AttachController.php#L42
