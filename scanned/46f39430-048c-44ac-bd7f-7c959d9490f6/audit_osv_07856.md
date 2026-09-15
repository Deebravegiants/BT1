# [H] NTLM Buffer Overflow

## Summary
Severity: High
Advisory: CURL-CVE-2005-3185
Aliases: CVE-2005-3185
Published: 2005-10-13
Source: https://osv.dev/vulnerability/CURL-CVE-2005-3185
Type: osv

## Details
libcurl's NTLM function can overflow a stack-based buffer if given a too long
username or domain name. This would happen if you enable NTLM authentication
and either:

 A - pass in a username and domain name to libcurl that together are longer
     than 192 bytes

 B - allow (lib)curl to follow HTTP "redirects" (Location: and the appropriate
     HTTP 30x response code) and the new URL contains a URL with a username
     and domain name that together are longer than 192 bytes
