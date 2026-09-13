# [C] SASL buffer overflow

## Summary
Severity: Critical
Advisory: CURL-CVE-2013-0249
Aliases: CVE-2013-0249
Published: 2013-02-06
Source: https://osv.dev/vulnerability/CURL-CVE-2013-0249
Type: osv

## Details
libcurl is vulnerable to a buffer overflow vulnerability when communicating
  with one of the protocols POP3, SMTP or IMAP.

  When negotiating SASL DIGEST-MD5 authentication, the function
  `Curl_sasl_create_digest_md5_message()` uses the data provided from the
  server without doing the proper length checks and that data is then appended
  to a local fixed-size buffer on the stack.

  This vulnerability can be exploited by someone who is in control of a server
  that a libcurl based program is accessing with POP3, SMTP or IMAP. For
  applications that accept user provided URLs, it is also thinkable that a
  malicious user would feed an application with a URL to a server hosting code
  targeting this flaw.

  This vulnerability can be used for remote code execution (RCE) on vulnerable
  systems.

  Both curl the command line tool and applications using the libcurl library
  are vulnerable.
