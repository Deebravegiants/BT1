# [H] Kroki Arbitrary File Read/Write 

## Summary
Severity: High
Program: GitLab
Weakness: Improper Access Control - Generic
Reporter: ledz1996
State: resolved
Disclosed: 2021-05-21T19:56:02.582Z
Source: https://hackerone.com/reports/1098793

## Details
### Summary

In short, I've found a potentially weird bug in `asciidoctor` that could lead to arbitrary file read/write in `asciidoctor-kroki` even though Gitlab have already made an attempt to disable `kroki-plantuml-include`

**lib/gitlab/asciidoc.rb**
```rb
module Gitlab
  # Parser/renderer for the AsciiDoc format that uses Asciidoctor and filters
  # the resulting HTML through HTML pipeline filters.
  module Asciidoc
    MAX_INCLUDE_DEPTH = 5
    MAX_INCLUDES = 32
    DEFAULT_ADOC_ATTRS = {
        'showtitle' => true,
        'sectanchors' => true,
        'idprefix' => 'user-content-',
        'idseparator' => '-',
        'env' => 'gitlab',
        'env-gitlab' => '',
        'source-highlighter' => 'gitlab-html-pipeline',
        'icons' => 'font',
        'outfilesuffix' => '.adoc',
        'max-include-depth' => MAX_INCLUDE_DEPTH,
        # This feature is disabled because it relies on File#read to read the file.
        # If we want to enable this feature we will need to provide a "GitLab compatible" implementation.
        # This attribute is typically used to share common config (skinparam...) across all PlantUML diagrams.
        # The value can be a path or a URL.
        'kroki-plantuml-include!' => '',
        # This feature is disabled because it relies on the local file system to save diagrams retrieved from the Kroki server.
        'kroki-fetch-diagram!' => ''
```

However this could easily be bypassed by using `counter`

https://github.com/asciidoctor/asciidoctor/blob/master/lib/asciidoctor/document.rb
```rb
  def counter name, seed = nil
    return @parent_document.counter name, seed if @parent_document
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1098793_
