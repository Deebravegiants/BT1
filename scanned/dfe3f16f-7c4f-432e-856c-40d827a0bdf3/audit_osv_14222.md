# [M] CVE-2018-8026

## Summary
Severity: Medium
Advisory: CVE-2018-8026
Aliases: GHSA-7px3-6f6g-hxcj
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-8026
Type: osv

## Details
This vulnerability in Apache Solr 6.0.0 to 6.6.4 and 7.0.0 to 7.3.1 relates to an XML external entity expansion (XXE) in Solr config files (currency.xml, enumsConfig.xml referred from schema.xml, TIKA parsecontext config file). In addition, Xinclude functionality provided in these config files is also affected in a similar way. The vulnerability can be used as XXE using file/ftp/http protocols in order to read arbitrary local files from the Solr server or the internal network. The manipulated files can be uploaded as configsets using Solr's API, allowing to exploit that vulnerability.

## References
- http://www.securityfocus.com/bid/104690
- https://mail-archives.apache.org/mod_mbox/lucene-solr-user/201807.mbox/%3C0cdc01d413b7%24f97ba580%24ec72f080%24%40apache.org%3E
- https://security.netapp.com/advisory/ntap-20190307-0002/
- https://issues.apache.org/jira/browse/SOLR-12450
