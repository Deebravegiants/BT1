# [H] CVE-2019-16263

## Summary
Severity: High
Advisory: CVE-2019-16263
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-10-07
Source: https://osv.dev/vulnerability/CVE-2019-16263
Type: osv

## Details
The Twitter Kit framework through 3.4.2 for iOS does not properly validate the api.twitter.com SSL certificate. Although the certificate chain must contain one of a set of pinned certificates, there are certain implementation errors such as a lack of hostname verification. NOTE: this is an end-of-life product.

## References
- https://blog.appicaptor.com/2019/10/04/vulnerable-library-warning-twitterkit-for-ios/
- https://github.com/twitter-archive/twitter-kit-ios/blob/ac42e1351a66afa5ff7718d04d64a905dafe1f41/TwitterCore/TwitterCore/Networking/Security/TWTRServerTrustEvaluator.m#L75-L81
- https://www.sit.fraunhofer.de/fileadmin/dokumente/CVE/Advisory_TwitterKit_for_iOS_CVE-2019-16263.pdf
