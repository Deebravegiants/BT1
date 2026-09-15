# [H] Micronaut vulnerable to DoS via crafted form-urlencoded body binding with descending array indices

## Summary
Severity: High
Advisory: GHSA-43w5-mmxv-cpvh
CVE: CVE-2026-33013
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-43w5-mmxv-cpvh
Type: github-advisory

## Affected
- Maven: `io.micronaut:micronaut-json-core` — affected >=4.0.0-M1 <4.10.16
- Maven: `io.micronaut:micronaut-json-core` — affected >=3.9.0 <3.10.5
- Maven: `io.micronaut:micronaut-json-core` — affected >=0 <3.8.13

## Details
In `JsonBeanPropertyBinder::expandArrayToThreshold` in `io.micronaut:micronaut-json-core` before Micronaut 4 4.10.16 and in Micronaut 3 before 3.10.5 does not correctly handle descending array index order during form-urlencoded body binding, which allows remote attackers to cause a denial of service (non-terminating loop, CPU exhaustion, and OutOfMemoryError) via crafted indexed form parameters (e.g., `authors[1].name` followed by `authors[0].name`).

### Example

With such an application

```java
package dosform;

import io.micronaut.http.HttpResponse;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Consumes;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Produces;

import java.net.URI;

@Controller
class HomeController {

    @Produces(MediaType.TEXT_HTML)
    @Get
    String index() {
        return """
                <!DOCTYPE html>
                <html>
                <head>
                <title></title>
                </head>
                <body>
    <form action="/submit" method="post">
      <label for="firstAuthor">Fist Author</label>
      <input id="firstAuthor" name="authors[0].name" type="text"/>

      <label for="secondAuthor">Second Author</label>
      <input id="secondAuthor" name="authors[1].name" type="text"/>
      
      <label for="thirdAuthor">Third Author</label>
      <input id="thirdAuthor" name="authors[2].name" type="text"/>

      <button type="submit">Submit</button>
    </form>
               
                </body>
                </html>
                """;
    }

    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    @Post("/submit")
    HttpResponse<?> submit(@Body Book book) {
        return HttpResponse.seeOther(URI.create("/"));
    }
}
package dosform;

import io.micronaut.core.annotation.Introspected;

import java.util.Objects;

@Introspected
public class Author {
    private String name;
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    @Override
    public final boolean equals(Object o) {
        if (!(o instanceof Author)) return false;

        Author author = (Author) o;
        return Objects.equals(name, author.name);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(name);
    }

    @Override
    public String toString() {
        return "Author{" +
                "name='" + name + '\'' +
                '}';
    }
}
package dosform;

import io.micronaut.core.annotation.Introspected;

import java.util.List;
import java.util.Objects;

@Introspected
public class Book {
    private List<Author> authors;
    public List<Author> getAuthors() { return authors; }
    public void setAuthors(List<Author> authors) { this.authors = authors; }

    @Override
    public final boolean equals(Object o) {
        if (!(o instanceof Book)) return false;

        Book book = (Book) o;
        return Objects.equals(authors, book.authors);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(authors);
    }

    @Override
    public String toString() {
        return "Book{" +
                "authors=" + authors +
                '}';
    }
}
```

Sending `curl -v -X POST 'http://127.0.0.1:8080/submit' -H 'Content-Type: application/x-www-form-urlencoded' --data-urlencode 'authors[1].name=RobertGalbraith' --data-urlencode 'authors[0].name=JKRowling'` causes sustained CPU usage and unbounded memory growth (eventually `OutOfMemoryError`). 

### Patches
For Micronaut 4, the problem has been patched in `micronaut-core`, dependencies with group id `io.micronaut`, since [4.10.16](https://github.com/micronaut-projects/micronaut-core/releases/tag/v4.10.16).

For Micronaut 3, the problem has been patched since [3.10.5](https://github.com/micronaut-projects/micronaut-core/releases/tag/v3.10.5)

Users upgrade to the latest version of the framework. 

### Workarounds
There is no way for users to fix or remediate the vulnerability without upgrading.

### References
PR Fix: https://github.com/micronaut-projects/micronaut-core/pull/12410

## References
- https://github.com/micronaut-projects/micronaut-core/security/advisories/GHSA-43w5-mmxv-cpvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33013
- https://github.com/micronaut-projects/micronaut-core/pull/12410
- https://github.com/micronaut-projects/micronaut-core/commit/1afe509677c51b320041b7a2c177366d4a4deb55
- https://github.com/micronaut-projects/micronaut-core
- https://github.com/micronaut-projects/micronaut-core/releases/tag/v3.10.5
- https://github.com/micronaut-projects/micronaut-core/releases/tag/v4.10.16
