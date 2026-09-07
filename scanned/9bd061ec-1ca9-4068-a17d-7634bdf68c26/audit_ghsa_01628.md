# [H] Local Temp Directory Hijacking Vulnerability

## Summary
Severity: High
Advisory: GHSA-g3wg-6mcf-8jj6
CVE: CVE-2020-27216
CWE: CWE-378, CWE-379, CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-11-04
Source: https://github.com/advisories/GHSA-g3wg-6mcf-8jj6
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-webapp` — affected >=0 <9.4.33.v20201020
- Maven: `org.mortbay.jetty:jetty-webapp` — affected >=0 <9.4.33
- Maven: `org.eclipse.jetty:jetty-webapp` — affected >=10.0.0.beta1 <10.0.0.beta3
- Maven: `org.mortbay.jetty:jetty-webapp` — affected >=10.0.0.beta1 <10.0.0.beta3
- Maven: `org.eclipse.jetty:jetty-webapp` — affected >=11.0.0.beta1 <11.0.0.beta3
- Maven: `org.mortbay.jetty:jetty-webapp` — affected >=11.0.0.beta1 <11.0.0.beta3

## Details
### Impact
On Unix like systems, the system's temporary directory is shared between all users on that system.  A collocated user can observe the process of creating a temporary sub directory in the shared temporary directory and race to complete the creation of the temporary subdirectory.  If the attacker wins the race then they will have read and write permission to the subdirectory used to unpack web applications, including their WEB-INF/lib jar files and JSP files.  If any code is ever executed out of this temporary directory, this can lead to a local privilege escalation vulnerability.

Additionally, any user code uses of [WebAppContext::getTempDirectory](https://www.eclipse.org/jetty/javadoc/9.4.31.v20200723/org/eclipse/jetty/webapp/WebAppContext.html#getTempDirectory()) would similarly be vulnerable.

Additionally, any user application code using the `ServletContext` attribute for the tempdir will also be impacted.
See: https://javaee.github.io/javaee-spec/javadocs/javax/servlet/ServletContext.html#TEMPDIR

For example:
```java
import java.io.File;
import java.io.IOException;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class ExampleServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        File tempDir = (File)getServletContext().getAttribute(ServletContext.TEMPDIR); // Potentially compromised
        // do something with that temp dir
    }
}
```

Example: The JSP library itself will use the container temp directory for compiling the JSP source into Java classes before executing them.

### CVSSv3.1 Evaluation

This vulnerability has been calculated to have a [CVSSv3.1 score of 7.8/10 (AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H&version=3.1)

### Patches
Fixes were applied to the 9.4.x branch with:
- https://github.com/eclipse/jetty.project/commit/53e0e0e9b25a6309bf24ee3b10984f4145701edb
- https://github.com/eclipse/jetty.project/commit/9ad6beb80543b392c91653f6bfce233fc75b9d5f

These will be included in releases: 9.4.33, 10.0.0.beta3, 11.0.0.beta3

### Workarounds

A work around is to set a temporary directory, either for the server or the context, to a directory outside of the shared temporary file system.
For recent releases, a temporary directory can be created simple by creating a directory called `work` in the ${jetty.base} directory (the parent directory of the `webapps` directory).
Alternately the java temporary directory can be set with the System Property `java.io.tmpdir`.    A more detailed description of how jetty selects a temporary directory is below.

The Jetty search order for finding a temporary directory is as follows:

1. If the [`WebAppContext` has a temp directory specified](https://www.eclipse.org/jetty/javadoc/current/org/eclipse/jetty/webapp/WebAppContext.html#setTempDirectory(java.io.File)), use it.
2. If the `ServletContext` has the `javax.servlet.context.tempdir` attribute set, and if directory exists, use it.
3. If a `${jetty.base}/work` directory exists, use it (since Jetty 9.1)
4. If a `ServletContext` has the `org.eclipse.jetty.webapp.basetempdir` attribute set, and if the directory exists, use it.
5. Use `System.getProperty("java.io.tmpdir")` and use it.

Jetty will end traversal at the first successful step.
To mitigate this vulnerability the directory must be set to one that is not writable by an attacker.  To avoid information leakage, the directory should also not be readable by an attacker.

#### Setting a Jetty server temporary directory.

Choices 3 and 5 apply to the server level, and will impact all deployed webapps on the server.

For choice 3  just create that work directory underneath your `${jetty.base}` and restart Jetty.

For choice 5, just specify your own `java.io.tmpdir` when you start the JVM for Jetty.

``` shell
[jetty-distribution]$ java -Djava.io.tmpdir=/var/web/work -jar start.jar
```

#### Setting a Context specific temporary directory.

The rest of the choices require you to configure the context for that deployed webapp (seen as `${jetty.base}/webapps/<context>.xml`)

Example (excluding the DTD which is version specific):

``` xml
<Configure class="org.eclipse.jetty.webapp.WebAppContext">
  <Set name="contextPath"><Property name="foo"/></Set>
  <Set name="war">/var/web/webapps/foo.war</Set>
  <Set name="tempDirectory">/var/web/work/foo</Set>
</Configure>
```

### References
 
 - https://github.com/eclipse/jetty.project/issues/5451
 - [CWE-378: Creation of Temporary File With Insecure Permissions](https://cwe.mitre.org/data/definitions/378.html)
 - [CWE-379: Creation of Temporary File in Directory with Insecure Permissions](https://cwe.mitre.org/data/definitions/379.html)
 - [CodeQL Query PR To Detect Similar Vulnerabilities](https://github.com/github/codeql/pull/4473)

### Similar Vulnerabilities

Similar, but not the same.

 - JUnit 4 - https://github.com/junit-team/junit4/security/advisories/GHSA-269g-pwp5-87pp
 - Google Guava - https://github.com/google/guava/issues/4011
 - Apache Ant - https://nvd.nist.gov/vuln/detail/CVE-2020-1945
 - JetBrains Kotlin Compiler - https://nvd.nist.gov/vuln/detail/CVE-2020-15824

### For more information

The original report of this vulnerability is below:

> On Thu, 15 Oct 2020 at 21:14, Jonathan Leitschuh <jonathan.leitschuh@gmail.com> wrote:
> Hi WebTide Security Team,
>
> I'm a security researcher writing some custom CodeQL queries to find Local Temporary Directory Hijacking Vulnerabilities. One of my queries flagged an issue in Jetty.
>
> https://lgtm.com/query/5615014766184643449/
>
> I've recently been looking into security vulnerabilities involving the temporary directory because on unix-like systems, the system temporary directory is shared between all users.
> There exists a race condition between the deletion of the temporary file and the creation of the directory.
>
> ```java
> // ensure file will always be unique by appending random digits
> tmpDir = File.createTempFile(temp, ".dir", parent); // Attacker knows the full path of the file that will be generated
> // delete the file that was created
> tmpDir.delete(); // Attacker sees file is deleted and begins a race to create their own directory before Jetty.
> // and make a directory of the same name
> // SECURITY VULNERABILITY: Race Condition! - Attacker beats Jetty and now owns this directory
> tmpDir.mkdirs();
> ```
>
> https://github.com/eclipse/jetty.project/blob/1b59672b7f668b8a421690154b98b4b2b03f254b/jetty-webapp/src/main/java/org/eclipse/jetty/webapp/WebInfConfiguration.java#L511-L518
>
> In several cases the `parent` parameter will not be the system temporary directory. However, there is one case where it will be, as the last fallback.
>
>
> https://github.com/eclipse/jetty.project/blob/1b59672b7f668b8a421690154b98b4b2b03f254b/jetty-webapp/src/main/java/org/eclipse/jetty/webapp/WebInfConfiguration.java#L467-L468
>
> If any code is ever executed out of this temporary directory, this can lead to a local privilege escalation vulnerability.
>
> Would your team be willing to open a GitHub security advisory to continue the discussion and disclosure there? https://github.com/eclipse/jetty.project/security/advisories
>
> **This vulnerability disclosure follows Google's [90-day vulnerability disclosure policy](https://www.google.com/about/appsecurity/) (I'm not an employee of Google, I just like their policy). Full disclosure will occur either at the end of the 90-day deadline or whenever a patch is made widely available, whichever occurs first.**
>
> Cheers,
> Jonathan Leitschuh

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-g3wg-6mcf-8jj6
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-g3wg-6mcf-8jj6#advisory-comment-63053
- https://nvd.nist.gov/vuln/detail/CVE-2020-27216
- https://github.com/eclipse/jetty.project/issues/5451
- https://github.com/github/codeql/pull/4473
- https://lists.apache.org/thread.html/raa9c370ab42d737e93bc1795bb6a2187d7c60210cd5e3b3ce8f3c484@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rad255c736fad46135f1339408cb0147d0671e45c376c3be85ceeec1a@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rae15d73cabef55bad148e4e6449b05da95646a2a8db3fc938e858dff@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/raf9c581b793c30ff8f55f2415c7bd337eb69775aae607bf9ed1b16fb@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rafb023a7c61180a1027819678eb2068b0b60cd5c2559cb8490e26c81@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rb077d35f2940191daeefca0d6449cddb2e9d06bcf8f5af4da2df3ca2@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rb5f2558ea2ac63633dfb04db1e8a6ea6bb1a2b8614899095e16c6233@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rb69b1d7008a4b3de5ce5867e41a455693907026bc70ead06867aa323@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rb7e159636b26156f6ef2b2a1a79b3ec9a026923b5456713e68f7c18e@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rb81a018f83fe02c95a2138a7bb4f1e1677bd7e1fc1e7024280c2292d@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rb8ad3745cb94c60d44cc369aff436eaf03dbc93112cefc86a2ed53ba@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rb8c007f87dc57731a7b9a3b05364530422535b7e0bc6a0c5b68d4d55@%3Cdev.felix.apache.org%3E
- https://lists.apache.org/thread.html/rbc5a622401924fadab61e07393235838918228b3d8a1a6704295b032@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rbc5a8d7a0a13bc8152d427a7e9097cdeb139c6cfe111b2f00f26d16b@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbf99e4495461099cad9aa62e0164f8f25a7f97b791b4ace56e375f8d@%3Cissues.beam.apache.org%3E
