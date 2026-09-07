# [M] DOS vulnerability for Quoted Quality CSV headers

## Summary
Severity: Medium
Advisory: GHSA-m394-8rww-3jr7
CVE: CVE-2020-27223
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-03-10
Source: https://github.com/advisories/GHSA-m394-8rww-3jr7
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.6 <9.4.37
- Maven: `org.eclipse.jetty:jetty-server` — affected >=10.0.0 <10.0.1
- Maven: `org.eclipse.jetty:jetty-server` — affected >=11.0.0 <11.0.1

## Details
### Impact
When Jetty handles a request containing request headers with a large number of “quality” (i.e. q) parameters (such as what are seen on the `Accept`, `Accept-Encoding`, and `Accept-Language` request headers), the server may enter a denial of service (DoS) state due to high CPU usage while sorting the list of values based on their quality values.  A single request can easily consume minutes of CPU time before it is even dispatched to the application.

The only features within Jetty that can trigger this behavior are:

- Default Error Handling - the `Accept` request header with the `QuotedQualityCSV` is used to determine what kind of content to send back to the client (html, text, json, xml, etc)
- `StatisticsServlet` - uses the `Accept` request header with the `QuotedQualityCSV` to determine what kind of content to send back to the client (xml, json, text, html, etc)
- `HttpServletRequest.getLocale()` - uses the `Accept-Language` request header with the `QuotedQualityCSV` to determine which “preferred” language is returned on this call.
- `HttpservletRequest.getLocales()` - is similar to the above, but returns an ordered list of locales based on the quality values on the `Accept-Language` request header.
- `DefaultServlet` - uses the `Accept-Encoding` request header with the `QuotedQualityCSV` to determine which kind of pre-compressed content should be sent back for static content (content that is not matched against a url-pattern in your web app)

### Versions
`QuotedQualityCSV` was introduced to Jetty 9.3.9.v20160517 and the bug that introduced the vulnerability was in 9.4.6.v20170531. 

Currently, known vulnerable versions include:

- 9.4.6.v20170531 thru to 9.4.36.v20210114
- 10.0.0
- 11.0.0

### Workarounds

Quality ordered values are used infrequently by jetty so they can be avoided by:

 * Do not use the default error page/handler.
 * Do not deploy the `StatisticsServlet` exposed to the network
 * Do not call `getLocale` API
 * Do not enable precompressed static content in the `DefaultServlet` 

### Patches

All patches are available for download from the Eclipse Jetty website at [https://www.eclipse.org/jetty/download.php](https://www.eclipse.org/jetty/download.php)
- 9.4.37.v20210219 and greater
- 10.0.1 and greater 
- 11.0.1 and greater

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-m394-8rww-3jr7
- https://nvd.nist.gov/vuln/detail/CVE-2020-27223
- https://lists.apache.org/thread.html/rd666e187ebea2fda8624683ab51e2a5ad2108f762d21bf1a383d7502@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rc721fe2910533bffb6bd4d69ea8ff4f36066d260dbcd2d14e041614a@%3Cissues.spark.apache.org%3E
- https://lists.apache.org/thread.html/rc052fd4e9e9c01bead74c0b5680355ea5dc3b72d46f253cb65d03e43@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rb79b62ac3085e05656e41865f5a7efcbdc7dcd7843abed9c5fe0fef8@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/raa6d60b00b67c0550672b4f506f0df75b323dcd25cf574e91e2f2dff@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra47a26c008487b0a739a368c846e168de06c3cd118d31ecedafa679a@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/ra40a88a2301a3da86e25b501ff4bc88124f2b816c2917d5f3497f8f0@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra384892bab8c03a60613a6a9d5e9cae0a2b800fd882792a55520115e@%3Ccommits.kafka.apache.org%3E
- https://lists.apache.org/thread.html/ra2f529da674f25a7351543544f7d621b5227c49a0745913b1194d11e@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/r8dc1b13b80d39fbf4a9d158850e15cd868f0460c2f364f13dca7050b@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r8b1963f16d6cb1230ca7ee73b6ec4f5c48f344191dbb1caabd265ee4@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r897a6a14d03eab09e89b809d2a650f3765065201da5bc3db9a4dd6e8@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r857b31ad16c6e76002bc6cca73c83358ed2595477e288286ee82c48d@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r855b24a3bde3674256152edfc53fb8c9000f9b59db3fecbbde33b211@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/r7ffd050d3bd7c90d95f4933560b5f4f15971ab9a5f5322fdce116243@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r7fbdb7880be1566f943d80fbbeefde2115c086eba1bef3115350a388@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rd8e24a3e482e5984bc8c5492dc790413e4fdc1234e3debb94515796b@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rdd6c47321db1bfe12c68a898765bf3b6f97e2afa6a501254ed4feaed@%3Cjira.kafka.apache.org%3E
