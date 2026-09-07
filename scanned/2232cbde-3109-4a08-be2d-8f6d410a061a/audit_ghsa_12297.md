# [M] jquery-ui Tooltip widget vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-qqxp-xp9v-vvx6
CVE: CVE-2012-6662
CWE: CWE-79
Ecosystem: Maven, NuGet, RubyGems, npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-qqxp-xp9v-vvx6
Type: github-advisory

## Affected
- npm: `jquery-ui` — affected >=0 <1.10.0
- RubyGems: `jquery-ui-rails` — affected >=0 <4.0.0
- Maven: `org.webjars.npm:jquery-ui` — affected >=0 <1.10.0
- NuGet: `jQuery.UI.Combined` — affected >=0 <1.10.0

## Details
Cross-site scripting (XSS) vulnerability in the default content option in jquery.ui.tooltip.js in the Tooltip widget in jQuery UI before 1.10.0 allows remote attackers to inject arbitrary web script or HTML via the title attribute, which is not properly handled in the autocomplete combo box demo.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6662
- https://github.com/jquery/jquery/issues/2432
- https://github.com/jquery/jquery-ui/commit/5fee6fd5000072ff32f2d65b6451f39af9e0e39e
- https://github.com/jquery/jquery-ui/commit/f2854408cce7e4b7fc6bf8676761904af9c96bde
- https://exchange.xforce.ibmcloud.com/vulnerabilities/98697
- https://github.com/jquery/jquery
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jquery-ui-rails/CVE-2012-6662.yml
- http://bugs.jqueryui.com/ticket/8859
- http://bugs.jqueryui.com/ticket/8861
- http://rhn.redhat.com/errata/RHSA-2015-0442.html
- http://rhn.redhat.com/errata/RHSA-2015-1462.html
- http://seclists.org/oss-sec/2014/q4/613
- http://seclists.org/oss-sec/2014/q4/616
