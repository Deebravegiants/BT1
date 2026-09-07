# [C] RCE via unsafe inline Kramdown options when rendering certain Wiki pages

## Summary
Severity: Critical
Program: GitLab
Weakness: Code Injection
Reporter: vakzz
State: resolved
Disclosed: 2021-04-20T17:35:23.805Z
Source: https://hackerone.com/reports/1125425

## Details
### Summary

When rendering wiki content with certain extensions such as `.rmd`,  `render_wiki_content` will call [`other_markup_unsafe`](https://gitlab.com/gitlab-org/gitlab/-/blob/v13.9.3-ee/app/helpers/markup_helper.rb#L145) which will end up calling `GitHub::Markup.render` from the `github-markup` gem.  Files with any extension can be uploaded by checking out the wiki with git, commiting the files and pushing the changes back.

Since `kramdown` is loaded, this will end up using it for the [markdown parser](https://github.com/github/markup/blob/v1.7.0/lib/github/markup/markdown.rb#L23) by calling `Kramdown::Document.new(content).to_html`

Kramdown has a special extension that allows for options to be [set inline](https://kramdown.gettalong.org/options.html), the example they give is: `{::options auto_ids="false" footnote_nr="5" syntax_highlighter_opts="{line_numbers: true\}" /}`

The default syntax highlighter is `rouge` which has an option [`formatter`](https://kramdown.gettalong.org/syntax_highlighter/rouge.html) that can be set via `syntax_highlighter_opts` in the inline options. This option gets used by [`formatter_class`](https://github.com/gettalong/kramdown/blob/REL_2_3_0/lib/kramdown/converter/syntax_highlighter/rouge.rb#L73):

```ruby
  def self.call(converter, text, lang, type, call_opts)
      opts = options(converter, type)
      call_opts[:default_lang] = opts[:default_lang]
      return nil unless lang || opts[:default_lang] || opts[:guess_lang]

      lexer = ::Rouge::Lexer.find_fancy(lang || opts[:default_lang], text)
      return nil if opts[:disable] || !lexer || (lexer.tag == "plaintext" && !opts[:guess_lang])

      opts[:css_class] ||= 'highlight' # For backward compatibility when using Rouge 2.0
      formatter = formatter_class(opts).new(opts)
      formatter.format(lexer.lex(text))
    end

  def self.formatter_class(opts = {})
      puts "formatter"
      puts opts[:formatter]
      case formatter = opts[:formatter]
      when Class
        formatter
      when /\A[[:upper:]][[:alnum:]_]*\z/
        ::Rouge::Formatters.const_get(formatter)
      else
        # Available in Rouge 2.0 or later
        ::Rouge::Formatters::HTMLLegacy
      end
    rescue NameError
      # Fallback to Rouge 1.x
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1125425_
