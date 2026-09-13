# [H] local file overwrite

## Summary
Severity: High
Advisory: CURL-CVE-2010-3842
Aliases: CVE-2010-3842
Published: 2010-10-13
Source: https://osv.dev/vulnerability/CURL-CVE-2010-3842
Type: osv

## Details
curl offers a command line option --remote-header-name (also usable as -J)
which uses the filename of the Content-disposition: header when it saves the
downloaded data locally.

curl attempts to cut off the directory parts from any given filename in the
header to only store files in the current directory. It might overwrite a
local file using the same name as the header specifies.

The stripping of the directory did not take backslashes into account. On
some operating systems, backslashes are used to separate directories and
filenames. This allows a rogue server to send back a response that
overwrites a filename in the local machine that the user is allowed to
write, potentially a system file, a command or a known executable.

Operating systems affected include Windows, Netware, MSDOS, OS/2 and
Symbian.

This error is only present in the curl command line tool, it is NOT a
problem of the library libcurl.
