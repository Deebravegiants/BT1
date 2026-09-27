# [M] iCalendar has ICS injection via unsanitized URI property values

## Summary
Severity: Medium
Advisory: GHSA-pv9c-9mfh-hvxq
CVE: CVE-2026-33635
CWE: CWE-93
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-pv9c-9mfh-hvxq
Type: github-advisory

## Affected
- RubyGems: `icalendar` — affected >=2.0.0 <2.12.2

## Details
### Summary
.ics serialization does not properly sanitize URI property values, enabling ICS injection through attacker-controlled input, adding arbitrary calendar lines to the output.

### Details
`Icalendar::Values::Uri` falls back to the raw input string when `URI.parse` fails and later serializes it with `value.to_s` without removing or escaping `\r` or `\n` characters. That value is embedded directly into the final ICS line by the normal serializer, so a payload containing CRLF can terminate the original property and create a new ICS property or component. (It looks like you can inject via url, source, image, organizer, attach, attendee, conference, tzurl because of this)

Relevant code:
- `lib/icalendar/values/uri.rb:16`

### PoC
Run the following with the library loaded:

```ruby
require "icalendar/value"
require "icalendar/values/uri"

v = Icalendar::Values::Uri.new("https://a.example/ok\r\nATTENDEE:mailto:evil@example.com")
puts v.to_ical(Icalendar::Values::Text)
```

output:

```text
;VALUE=URI:https://a.example/ok
ATTENDEE:mailto:evil@example.com
```

### Impact
Applications that generate `.ics` files from partially untrusted metadata are impacted. As a result, downstream calendar clients or importers may process attacker-supplied content as if it were legitimate event data, such as added attendees, modified URLs, alarms, or other calendar fields.

## Fix
Reject raw CR and LF characters in `URI`-typed values before serialization, or escape/encode them so they cannot terminate the current ICS content line.

## References
- https://github.com/icalendar/icalendar/security/advisories/GHSA-pv9c-9mfh-hvxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33635
- https://github.com/icalendar/icalendar/commit/b8d23b490363ee5fffaec1d269a8618a912ca265
- https://github.com/icalendar/icalendar
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/icalendar/CVE-2026-33635.yml
