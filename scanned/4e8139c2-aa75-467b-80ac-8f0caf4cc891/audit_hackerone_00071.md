# [H] Argument/Code Injection via ActiveStorage's image transformation functionality

## Summary
Severity: High
Program: Ruby on Rails
Weakness: Code Injection
Reporter: gquadros_
State: resolved
Disclosed: 2023-07-28T00:45:12.641Z
CVE: CVE-2022-21831
Source: https://hackerone.com/reports/1154034

## Details
# Affected components

Tested on:

1. activestorage 6.1.3.1
2. image\_processing 1.12.1
3. mini\_magick 4.11.0

# Found by

Gabriel Quadros and Ricardo Silva from Conviso Application Security

# Description

## Intro

ActiveStorage has an image transformation functionality [1, 2, 3, 4, 5, 6] which uses the concept of *variants*. By their own words [5]:

> Image blobs can have variants that are the result of a set of transformations applied to the original. These variants are used to create thumbnails, fixed-size avatars, or any other derivative image from the original.

> Variants rely on ImageProcessing gem for the actual transformations of the file, so you must add gem "image\_processing" to your Gemfile if you wish to use variants. By default, images will be processed with ImageMagick using the MiniMagick gem, but you can also switch to the libvips processor operated by the ruby-vips gem).

One example of direct usage can be seen in the docs as:

```ruby
<%= image_tag user.avatar.variant(resize_to_limit: [100, 100]) %>
```

This will create an image tag with a variant URL, which when visited will return the *avatar* image transformed to the new size.

Another example uses the *preview()* method, which can be used to generate images from videos and PDF files. Once the preview image is generated, it also calls *variant()* under the hood.

```html
<ul>
  <% @message.files.each do |file| %>
    <li>
      <%= image_tag file.preview(resize_to_limit: [100, 100]) %>
    </li>
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1154034_
