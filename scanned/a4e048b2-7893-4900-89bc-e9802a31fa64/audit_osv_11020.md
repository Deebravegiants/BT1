# [H] CVE-2017-5647

## Summary
Severity: High
Advisory: CVE-2017-5647
Aliases: GHSA-3gv7-3h64-78cm
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-04-17
Source: https://osv.dev/vulnerability/CVE-2017-5647
Type: osv

## Details
A bug in the handling of the pipelined requests in Apache Tomcat 9.0.0.M1 to 9.0.0.M18, 8.5.0 to 8.5.12, 8.0.0.RC1 to 8.0.42, 7.0.0 to 7.0.76, and 6.0.0 to 6.0.52, when send file was used, results in the pipelined request being lost when send file processing of the previous request completed. This could result in responses appearing to be sent for the wrong request. For example, a user agent that sent requests A, B and C could see the correct response for request A, the response for request C for request B and no response for request C.

## References
- http://www.arubanetworks.com/assets/alert/HPESBHF03730.txt
- http://www.securitytracker.com/id/1038218
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03730en_us
- https://lists.apache.org/thread.html/343558d982879bf88ec20dbf707f8c11255f8e219e81d45c4f8d0551%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/37220405a377c0182d2afdbc36461c4783b2930fbeae3a17f1333113%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/388a323769f1dff84c9ec905455aa73fbcb20338e3c7eb131457f708%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/39ae1f0bd5867c15755a6f959b271ade1aea04ccdc3b2e639dcd903b%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/3d19773b4cf0377db62d1e9328bf9160bf1819f04f988315086931d7%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/5796678c5a773c6f3ff57c178ac247d85ceca0dee9190ba48171451a%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/5c0e00fd31efc11e147bf99d0f03c00a734447d3b131ab0818644cdb%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/6af47120905aa7d8fe12f42e8ff2284fb338ba141d3b77b8c7cb61b3%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/845312a10aabbe2c499fca94003881d2c79fc993d85f34c1f5c77424%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/88855876c33f2f9c532ffb75bfee570ccf0b17ffa77493745af9a17a%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b5e3f51d28cd5d9b1809f56594f2cf63dcd6a90429e16ea9f83bbedc%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b84ad1258a89de5c9c853c7f2d3ad77e5b8b2930be9e132d5cef6b95%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b8a1bf18155b552dcf9a928ba808cbadad84c236d85eab3033662cfb%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r03c597a64de790ba42c167efacfa23300c3d6c9fe589ab87fe02859c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0%40%3Cdev.tomcat.apache.org%3E
