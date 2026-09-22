# [M] FTP wildcard stack overflow

## Summary
Severity: Medium
Advisory: CURL-CVE-2020-8285
Aliases: CVE-2020-8285
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CURL-CVE-2020-8285
Type: osv

## Details
libcurl offers a wildcard matching functionality, which allows a callback (set
with `CURLOPT_CHUNK_BGN_FUNCTION`) to return information back to libcurl on
how to handle a specific entry in a directory when libcurl iterates over a
list of all available entries.

When this callback returns `CURL_CHUNK_BGN_FUNC_SKIP`, to tell libcurl to not
deal with that file, the internal function in libcurl then calls itself
recursively to handle the next directory entry.

If there is a sufficient amount of file entries and if the callback returns
"skip" enough number of times, libcurl runs out of stack space. The exact
amount does of course vary with platforms, compilers and other environmental
factors.

The content of the remote directory is not kept on the stack, so it seems hard
for the attacker to control exactly what data that overwrites the stack -
however it remains a Denial-Of-Service vector as a malicious user who controls
a server that a libcurl-using application works with under these premises can
trigger a crash.

(There is also a few other ways the function can be made to call itself and
trigger this problem.)
