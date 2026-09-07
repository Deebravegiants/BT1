# [M] Cross-site Scripting in Jenkins Rebuilder Plugin

## Summary
Severity: Medium
Advisory: GHSA-7m8v-w6f9-q2f9
CVE: CVE-2018-1000415
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7m8v-w6f9-q2f9
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.hudson.plugins.rebuild:rebuild` — affected >=0 <1.29

## Details
A cross-site scripting vulnerability exists in Jenkins Rebuilder Plugin 1.28 and earlier in 
```
RebuildAction/BooleanParameterValue.jelly,  
RebuildAction/ExtendedChoiceParameterValue.jelly,  
RebuildAction/FileParameterValue.jelly,  
RebuildAction/LabelParameterValue.jelly,  
RebuildAction/ListSubversionTagsParameterValue.jelly,  
RebuildAction/MavenMetadataParameterValue.jelly,  
RebuildAction/NodeParameterValue.jelly,  
RebuildAction/PasswordParameterValue.jelly,  
RebuildAction/RandomStringParameterValue.jelly,  
RebuildAction/RunParameterValue.jelly,  
RebuildAction/StringParameterValue.jelly,  
RebuildAction/TextParameterValue.jelly,  
RebuildAction/ValidatingStringParameterValue.jelly  
```
that allows users with Job/Configuration permission to insert arbitrary HTML into rebuild forms.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000415
- https://github.com/jenkinsci/rebuild-plugin/commit/3a4ca33a45fa048c9ab7b7082f87e72c0df848cb
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-130
- http://www.securityfocus.com/bid/106532
