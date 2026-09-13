# [M] CVE-2017-0911

## Summary
Severity: Medium
Advisory: CVE-2017-0911
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2017-0911
Type: osv

## Details
Twitter Kit for iOS versions 3.0 to 3.2.1 is vulnerable to a callback verification flaw in the "Login with Twitter" component allowing an attacker to provide alternate credentials. In the final step of "Login with Twitter" authentication information is passed back to the application using the registered custom URL scheme (typically twitterkit-<consumer-key>) on iOS. Because the callback handler did not verify the authenticity of the response, this step is vulnerable to forgery, potentially allowing attacker to associate a Twitter account with a third-party service.

## References
- https://blog.twitter.com/developer/en_us/topics/tips/2018/vulnerability-in-twitter-kit-for-ios.html
- https://github.com/twitter/twitter-kit-ios/wiki/Changelog#322-november-28-2017
- https://hackerone.com/reports/290229
- https://github.com/twitter/twitter-kit-ios/blob/b6eb49d149b056d826cbc4b53eaeb39a3ebd591e/TwitterKit/TwitterKit/Social/Identity/TWTRMobileSSO.m#L71
- https://github.com/twitter/twitter-kit-ios/blob/b6eb49d149b056d826cbc4b53eaeb39a3ebd591e/TwitterKit/TwitterKit/TWTRTwitter.m#L411
