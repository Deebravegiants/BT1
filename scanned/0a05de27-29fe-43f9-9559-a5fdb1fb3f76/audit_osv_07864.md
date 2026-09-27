# [M] cookie leak with IP address as domain

## Summary
Severity: Medium
Advisory: CURL-CVE-2014-3613
Aliases: CVE-2014-3613
Published: 2014-09-10
Source: https://osv.dev/vulnerability/CURL-CVE-2014-3613
Type: osv

## Details
By not detecting and rejecting domain names for partial literal IP addresses
properly when parsing received HTTP cookies, libcurl can be fooled to both
sending cookies to wrong sites and into allowing arbitrary sites to set
cookies for others.

For this problem to trigger, the client application must use the numerical
IP address in the URL to access the site and the site must send back cookies
to the site using domain= and a partial IP address.

Since libcurl wrongly approaches the IP address like it was a normal domain
name, a site at IP address `192.168.0.1` can set cookies for anything ending
with `.168.0.1` thus fooling libcurl to send them also to for example
`129.168.0.1`.

The flaw requires dots to be present in the IP address, which restricts the
flaw to IPv4 literal addresses or IPv6 addresses using the somewhat unusual
"dotted-quad" style: `::ffff:192.0.2.128`.

This is not believed to be done by typical sites as this is not supported by
clients that adhere to the rules of the RFC 6265, and many sites are written
to explicitly use their own specific named domain when sending cookies.
