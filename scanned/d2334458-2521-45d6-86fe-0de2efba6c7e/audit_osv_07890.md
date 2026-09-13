# [M] SSL_VERIFYSTATUS ignored

## Summary
Severity: Medium
Advisory: CURL-CVE-2017-2629
Aliases: CVE-2017-2629
Published: 2017-02-22
Source: https://osv.dev/vulnerability/CURL-CVE-2017-2629
Type: osv

## Details
curl and libcurl support "OCSP stapling", also known as the TLS Certificate
Status Request extension (using the `CURLOPT_SSL_VERIFYSTATUS` option). When
telling curl to use this feature, it uses that TLS extension to ask for a
fresh proof of the server's certificate's validity. If the server does not
support the extension, or fails to provide said proof, curl is expected to
return an error.

Due to a coding mistake, the code that checks for a test success or failure,
ends up always thinking there is valid proof, even when there is none or if
the server does not support the TLS extension in question. Contrary to how it
used to function and contrary to how this feature is documented to work.

This could lead to users not detecting when a server's certificate goes
invalid or otherwise be mislead that the server is in a better shape than it
is in reality.

This flaw also exists in the command line tool
([--cert-status](https://curl.se/docs/manpage.html#--cert-status)).
