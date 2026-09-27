# [H] user/group information can be corrupted across storing in fsimage and reading back from fsimage

## Summary
Severity: High
Advisory: GHSA-hx83-rpqf-m267
CVE: CVE-2018-11768
CWE: CWE-119
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-11-20
Source: https://github.com/advisories/GHSA-hx83-rpqf-m267
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-main` — affected >=2.2.0 <2.8.5
- Maven: `org.apache.hadoop:hadoop-main` — affected >=2.9.0 <2.9.2
- Maven: `org.apache.hadoop:hadoop-main` — affected >=3.0.0 <3.1.1

## Details
In Apache Hadoop 3.1.0 to 3.1.1, 3.0.0-alpha1 to 3.0.3, 2.9.0 to 2.9.1, and 2.0.0-alpha to 2.8.4, the user/group information can be corrupted across storing in fsimage and reading back from fsimage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11768
- https://hadoop.apache.org/cve_list.html
- https://lists.apache.org/thread.html/2067a797b330530a6932f4b08f703b3173253d0a2b7c8c524e54adaf@%3Cgeneral.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/2c9cc65864be0058a5d5ed2025dfb9c700bf23d352b0c826c36ff96a@%3Chdfs-dev.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/72ca514e01cd5f08151e74f9929799b4cbe1b6e9e6cd24faa72ffcc6@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/9b609d4392d886711e694cf40d86f770022baf42a1b1aa97e8244c87@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/caacbbba2dcc1105163f76f3dfee5fbd22e0417e0783212787086378@%3Cgeneral.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/ceb16af9139ab0fea24aef935b6321581976887df7ad632e9a515dda@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/ea6d2dfbefab8ebe46be18b05136b83ae53b7866f1bc60c680a2b600@%3Chdfs-dev.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/f20bb4e055d8394fc525cc7772fb84096f706389043e76220c8a29a4@%3Chdfs-dev.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r02e39d7beb32eebcdbb4b516e95f67d71c90d5d462b26f4078d21eeb@%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r02e39d7beb32eebcdbb4b516e95f67d71c90d5d462b26f4078d21eeb@%3Cuser.flink.apache.org%3E
