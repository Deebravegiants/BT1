# [C] Improper Access Control in SLF4J

## Summary
Severity: Critical
Advisory: GHSA-w77p-8cfg-2x43
CVE: CVE-2018-8088
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w77p-8cfg-2x43
Type: github-advisory

## Affected
- Maven: `org.slf4j:slf4j-ext` — affected >=0 <1.7.26
- Maven: `org.slf4j:slf4j-ext` — affected >=1.8.0-alpha0 <1.8.0-beta4

## Details
org.slf4j.ext.EventData in the slf4j-ext module in QOS.CH SLF4J before `1.8.0-beta4` allows remote attackers to bypass intended access restrictions via crafted data. EventData in the slf4j-ext module in QOS.CH SLF4J, has been fixed in SLF4J version `1.7.26` and later and in the `2.0.x` series.

Note that while the [fix commit](https://github.com/qos-ch/slf4j/commit/d2b27fba88e983f921558da27fc29b5f5d269405) is associated with the tag `1.8.0-beta3`, the versions in [Maven](https://mvnrepository.com/artifact/org.slf4j/slf4j-ext) go directly from `1.8.0-beta2` to `1.8.0-beta4`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8088
- https://github.com/qos-ch/slf4j/commit/d2b27fba88e983f921558da27fc29b5f5d269405
- https://lists.apache.org/thread.html/rc378b97d52856f9f3c5ced14771fed8357e4187a3a0f9a2f0515931a@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rc378b97d52856f9f3c5ced14771fed8357e4187a3a0f9a2f0515931a%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/raabf1a00b2652575fca9fcb44166a828a0cab97a7d1594001eabc991@%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/raabf1a00b2652575fca9fcb44166a828a0cab97a7d1594001eabc991%40%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r9e25496608036573736cee484d8d03dae400f09e443b0000b6adc042@%3Ccommits.iotdb.apache.org%3E
- https://lists.apache.org/thread.html/r9e25496608036573736cee484d8d03dae400f09e443b0000b6adc042%40%3Ccommits.iotdb.apache.org%3E
- https://lists.apache.org/thread.html/r99a6552e45ca6ba1082031421f51799a4a665eda905ab2c2aa9d6ffa@%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r99a6552e45ca6ba1082031421f51799a4a665eda905ab2c2aa9d6ffa%40%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r9584c4304c888f651d214341a939bd264ed30c9e3d0d30fe85097ecf@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r9584c4304c888f651d214341a939bd264ed30c9e3d0d30fe85097ecf%40%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r891761d5014f9ffd79d9737482de832462de538b6c4bdcef21aad729@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r891761d5014f9ffd79d9737482de832462de538b6c4bdcef21aad729%40%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r81711cde77c2c5742b7b8533c978e79771b700af0ef4d3149d70df25@%3Cnotifications.logging.apache.org%3E
- https://lists.apache.org/thread.html/r81711cde77c2c5742b7b8533c978e79771b700af0ef4d3149d70df25%40%3Cnotifications.logging.apache.org%3E
- https://lists.apache.org/thread.html/r767861f053c15f9e9201b939a0d508dd58475a072e76135eaaca17f0@%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r767861f053c15f9e9201b939a0d508dd58475a072e76135eaaca17f0%40%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r5cf87a035b297c19f4043a37b73c341576dd92f819bd3e4aa27de541@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r5cf87a035b297c19f4043a37b73c341576dd92f819bd3e4aa27de541%40%3Cissues.flink.apache.org%3E
