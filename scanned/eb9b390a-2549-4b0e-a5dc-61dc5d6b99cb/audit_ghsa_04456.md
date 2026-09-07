# [H] Gogs has Stored XSS in `.ipynb` Preview

## Summary
Severity: High
Advisory: GHSA-jq8v-rmf6-65jw
CVE: CVE-2026-52798
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-jq8v-rmf6-65jw
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
# Summary

Although `.ipynb` previews are sanitized on the server side via `/-/api/sanitize_ipynb`, the inserted content is **re-rendered on the client side without sanitization** using `marked()` on elements with the `.nb-markdown-cell` class. During this process, links containing schemes such as `javascript:` can be regenerated.

As a result, when a victim views an attacker-crafted `.ipynb` file and clicks the link, **arbitrary JavaScript is executed in the Gogs origin**, leading to a click-based Stored XSS.

# Details

After the rendered output of a `.ipynb` file is sanitized via `/-/api/sanitize_ipynb` and inserted into the DOM, **only the Markdown cell portions are re-rendered using `marked()` and overwritten in the DOM**. During this process, links with the `javascript:` scheme can be regenerated.

`templates/repo/view_file.tmpl:42–71`

```html
{{else if .IsIPythonNotebook}}
  <script>
    $.getJSON("{{.RawFileLink}}", null, function(notebook_json) {
      var notebook = nb.parse(notebook_json);
      var rendered = notebook.render();
      $.ajax({
        type: "POST",
        url: '{{AppSubURL}}/-/api/sanitize_ipynb',
        data: rendered.outerHTML,
        processData: false,
        contentType: false,
      }).done(function(data) {
        $("#ipython-notebook").append(data);
        $("#ipython-notebook code").each(function(i, block) {
          $(block).addClass("py").addClass("python");
          hljs.highlightBlock(block);
        });

        // Overwrite image method to append proper prefix to the source URL
        var renderer = new marked.Renderer();
        var context = '{{.RawFileLink}}';
        context = context.substring(0, context.lastIndexOf("/"));
        renderer.image = function (href, title, text) {
          return `<img src="${context}/${href}"`
        };
        $("#ipython-notebook .nb-markdown-cell").each(function(i, markdown) {
          $(markdown).html(marked($(markdown).html(), {renderer: renderer}));
        });
      });
    });
  </script>
```

While **regular HTML pages (including `.ipynb` preview pages)** are served **without a Content Security Policy (CSP)**, CSP headers are applied **only to attachment delivery routes**.

`internal/cmd/web.go:323`

```go
c.Header().Set("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; sandbox")
```


# Steps to Reproduce

1. As the attacker, add and push/commit a `.ipynb` file containing a `javascript:` link in a Markdown cell to a repository.

   * Example (PoC):

     ```json
     {
       "nbformat": 4,
       "nbformat_minor": 2,
       "metadata": {},
       "cells": [
         {
           "cell_type": "markdown",
           "metadata": {},
           "source": [
             "[poc](javascript:alert(document.domain))"
           ]
         }
       ]
     }
     ```

2. The victim opens the file on Gogs (e.g., `/<user>/<repo>/src/<branch>/poc.ipynb`).
<img width="2386" height="1218" alt="image" src="https://github.com/user-attachments/assets/b0d93fd8-c5ca-4058-8af0-98dee590d3ad" />

3. When the victim clicks the `poc` link displayed in the preview, `alert(document.domain)` is executed in the same Gogs origin.
<img width="2390" height="1388" alt="image" src="https://github.com/user-attachments/assets/0eb6ebe8-632c-4a41-8a11-46471514b4c4" />

# Minimum Required Privileges

* **Attacker**: Ability to place a `.ipynb` file as a **regular (non-admin) user**

  * For example: a general user who can create a public repository and add files.
  * Or: write access (collaborator, etc.) to an existing repository that the victim will view.
* **Victim**: Permission to view the repository (a click is required).

# Impact

* Unauthorized actions performed with the victim’s account privileges (e.g., repository settings changes, Issue operations,誘導 to token creation).
* Theft of information accessible to the victim (repository/Issue/Wiki contents, tokens exposed in page context).
* If the victim is an administrator, the impact may escalate to instance-wide configuration changes and user management.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-jq8v-rmf6-65jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-52798
- https://github.com/gogs/gogs/pull/8319
- https://github.com/gogs/gogs/commit/17b168b11ca759a7550e1f4bbd68bbde14db7785
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
