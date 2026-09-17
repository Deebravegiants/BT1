# [H] Commons FileUpload Denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-xx68-jfcg-xmmf
CVE: CVE-2014-0050
CWE: CWE-20
Ecosystem: Maven
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-xx68-jfcg-xmmf
Type: github-advisory

## Affected
- Maven: `commons-fileupload:commons-fileupload` — affected >=0 <1.3.1
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0-RC1 <8.0.3
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.52

## Details
MultipartStream.java in Apache Commons FileUpload before 1.3.1, as used in Apache Tomcat, JBoss Web, and other products, allows remote attackers to cause a denial of service (infinite loop and CPU consumption) via a crafted Content-Type header that bypasses a loop's intended exit conditions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0050
- https://github.com/apache/commons-fileupload/commit/c61ff05b3241cb14d989b67209e57aa71540417a
- https://github.com/apache/tomcat/commit/29384723d8d9645b87e05be9fa369a4deeb78b9c
- https://bugzilla.redhat.com/show_bug.cgi?id=1062337
- https://github.com/advisories/GHSA-xx68-jfcg-xmmf
- https://github.com/apache/commons-fileupload
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05324755
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05376917
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05390722
- https://svn.apache.org/viewvc?view=revision&revision=1565143
- https://svn.apache.org/viewvc?view=revision&revision=1565163
- https://svn.apache.org/viewvc?view=revision&revision=1565169
- https://tomcat.apache.org/security-7.html
- https://tomcat.apache.org/security-8.html
- http://advisories.mageia.org/MGASA-2014-0110.html
- http://blog.spiderlabs.com/2014/02/cve-2014-0050-exploit-with-boundaries-loops-without-boundaries.html
- http://jvn.jp/en/jp/JVN14876762/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2014-000017
- http://mail-archives.apache.org/mod_mbox/commons-dev/201402.mbox/%3C52F373FC.9030907@apache.org%3E
- http://marc.info/?l=bugtraq&m=143136844732487&w=2
