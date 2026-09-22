# [M] Metalink download sends credentials

## Summary
Severity: Medium
Advisory: CURL-CVE-2021-22923
Aliases: CVE-2021-22923
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CURL-CVE-2021-22923
Type: osv

## Details
When curl is instructed to get content using the Metalink feature, and a user
name and password are used to download the Metalink XML file, those same
credentials are then subsequently passed on to each of the servers from which
curl downloads or tries to download the contents from. Often contrary to the
user's expectations and intentions and without telling the user it happened.
