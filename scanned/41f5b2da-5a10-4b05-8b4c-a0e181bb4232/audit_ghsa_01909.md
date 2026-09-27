# [H] ReDos vulnerability on guest checkout email validation

## Summary
Severity: High
Advisory: GHSA-qxmr-qxh6-2cc9
CVE: CVE-2021-43805
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-07
Source: https://github.com/advisories/GHSA-qxmr-qxh6-2cc9
Type: github-advisory

## Affected
- RubyGems: `solidus_core` — affected >=0 <2.11.13
- RubyGems: `solidus_core` — affected >=3.0.0 <3.0.4
- RubyGems: `solidus_core` — affected >=3.1.0 <3.1.4

## Details
### Impact
Denial of service vulnerability that could be exploited during a guest checkout. The regular expression used to validate a guest order's email was subject to exponential backtracking through a fragment like `a.a.`.

Before the patch, it can be reproduced in the console like this:

```ruby
irb(main)> Spree::EmailValidator::EMAIL_REGEXP.match "a@a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.@"
processing time: 54.293660s
=> nil
```

To reproduce in the browser, fill in the "Customer Email" field with that fake email address during a guest checkout. Before that, you should open the browser dev tools and change the `type` attribute for that field from `email` to `text`. After entering a fake address and pressing the "Save & Continue" button, the browser will take a long term to perform the request before showing an error message for the invalid address. Eventually, making the email string even longer could lead to the exhaustion of server resources.


### Patches
Versions 3.1.4, 3.0.4, and 2.11.13 have been patched to use a different regular expression.

There's an improbable chance that some orders in your system end up having associated an email address that is no longer valid. We've added a task to check precisely that:

```bash
bin/rails solidus:check_orders_with_invalid_email
```

The above will print information for every affected order if any.

### Workarounds

If a prompt upgrade is not an option, please, add the following to `config/application.rb`:

```ruby
config.after_initialize do
  Spree::EmailValidator.send(:remove_const, :EMAIL_REGEXP)
  Spree::EmailValidator::EMAIL_REGEXP = URI::MailTo::EMAIL_REGEXP
end
```

### References

- https://en.wikipedia.org/wiki/ReDoS
- https://snyk.io/blog/redos-and-catastrophic-backtracking/

### For more information
If you have any questions or comments about this advisory:
* Open an [issue](https://github.com/solidusio/solidus/issues) or a [discussion](https://github.com/solidusio/solidus/discussions) in Solidus.
* Email us at [security@solidus.io](mailto:security@soliidus.io)
* Contact the core team on [Slack](http://slack.solidus.io/)

## References
- https://github.com/solidusio/solidus/security/advisories/GHSA-qxmr-qxh6-2cc9
- https://nvd.nist.gov/vuln/detail/CVE-2021-43805
- https://github.com/solidusio/solidus/commit/6be174c955fad84017ca67589c676526bc5ade71
- https://github.com/solidusio/solidus/commit/9867153e01e3c3b898cdbcedd7b43375ea922401
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/solidus_core/CVE-2021-43805.yml
- https://github.com/solidusio/solidus
