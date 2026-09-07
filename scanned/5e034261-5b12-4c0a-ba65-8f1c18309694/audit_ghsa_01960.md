# [M] Cross-site scripting in Apache HttpClient

## Summary
Severity: Medium
Advisory: GHSA-7r82-7xv7-xcpj
CVE: CVE-2020-13956
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-06-03
Source: https://github.com/advisories/GHSA-7r82-7xv7-xcpj
Type: github-advisory

## Affected
- Maven: `org.apache.httpcomponents:httpclient` — affected >=0 <4.5.13
- Maven: `org.apache.httpcomponents:httpclient` — affected >=5.0.0 <5.0.3

## Details
Apache HttpClient versions prior to version 4.5.13 and 5.0.3 can misinterpret malformed authority component in request URIs passed to the library as java.net.URI object and pick the wrong target host for request execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13956
- https://lists.apache.org/thread.html/re504acd4d63b8df2a7353658f45c9a3137e5f80e41cf7de50058b2c1@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/rd5ab56beb2ac6879f6ab427bc4e5f7691aed8362d17b713f61779858@%3Cissues.hive.apache.org%3E
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rcd9ad5dda60c82ab0d0c9bd3e9cb1dc740804451fc20c7f451ef5cc4@%3Cgitbox.hive.apache.org%3E
- https://lists.apache.org/thread.html/rcced7ed3237c29cd19c1e9bf465d0038b8b2e967b99fc283db7ca553@%3Cdev.ranger.apache.org%3E
- https://lists.apache.org/thread.html/rc990e2462ec32b09523deafb2c73606208599e196fa2d7f50bdbc587@%3Cissues.maven.apache.org%3E
- https://lists.apache.org/thread.html/rc5c6ccb86d2afe46bbd4b71573f0448dc1f87bbcd5a0d8c7f8f904b2@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rc505fee574fe8d18f9b0c655a4d120b0ae21bb6a73b96003e1d9be35@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/rc3739e0ad4bcf1888c6925233bfc37dd71156bbc8416604833095c42@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/rc0863892ccfd9fd0d0ae10091f24ee769fb39b8957fe4ebabfc11f17@%3Cdev.jackrabbit.apache.org%3E
- https://lists.apache.org/thread.html/rb725052404fabffbe093c83b2c46f3f87e12c3193a82379afbc529f8@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rb4ba262d6f08ab9cf8b1ebbcd9b00b0368ffe90dad7ad7918b4b56fc@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/rb33212dab7beccaf1ffef9b88610047c644f644c7a0ebdc44d77e381@%3Ccommits.turbine.apache.org%3E
- https://lists.apache.org/thread.html/rae14ae25ff4a60251e3ba2629c082c5ba3851dfd4d21218b99b56652@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/rad6222134183046f3928f733bf680919e0c390739bfbfe6c90049673@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/ra8bc6b61c5df301a6fe5a716315528ecd17ccb8a7f907e24a47a1a5e@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rea3dbf633dde5008d38bf6600a3738b9216e733e03f9ff7becf79625@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/ree942561f4620313c75982a4e5f3b74fe6f7062b073210779648eec2@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/reef569c2419705754a3acf42b5f19b2a158153cef0e448158bc54917@%3Cdev.drill.apache.org%3E
