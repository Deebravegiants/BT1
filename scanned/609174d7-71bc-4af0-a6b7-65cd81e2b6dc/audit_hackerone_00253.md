# [M] Access to all files of remote user through shared file

## Summary
Severity: Medium (CVSS 6.8)
Program: Nextcloud
Weakness: Information Disclosure
Reporter: xuesheng
State: resolved
Disclosed: 2020-03-01T14:10:12.955Z
Source: https://hackerone.com/reports/258084

## Details
### Steps to reproduce
1. User A shares a file "movie.mp4" with user B.
2. User B uses webdav to access files (e.g. foldersync or nautilus)
3. share is shown as regular file (using webdav).
4. Copy the file and paste it to the same folder (still using webdav).
5. A new folder will appear with the name "(1)movie.mp4". This folder contains all data of user A (which is quite scary). Folder structure looks like: files, files_trashbin, cache, etc. (all user related files).
6. I was able to reproduce this with different combination of users and shared files.

### Expected behaviour
Only the shared file should be copied.

### Actual behaviour
All files of remote user are copied.

### Server configuration

**Operating system**: Ubuntu 16.04.3 LTS

**Web server:** apache2 (2.4.18-2ubuntu3)

**Database:** mariadb (10.0.24-7)

**PHP version:** php7 (7.0+35ubuntu6)

**Nextcloud version:** 12.0.1

**Updated from an older Nextcloud/ownCloud or fresh install:** originally owncloud, upgradepath according to the official documentation to nextcloud (owncloud 9 to nextcloud 9 or 10, can't remember).

**Where did you install Nextcloud from:** Nextcloud package was downloaded from official webpage (nextcloud.com)

**Signing status:**
<details>
<summary>Signing status</summary>

```
No errors have been found.
```
</details>

_Trimmed to 38 lines — full report: https://hackerone.com/reports/258084_
