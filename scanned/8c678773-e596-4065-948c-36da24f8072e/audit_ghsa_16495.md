# [H] Symfony Cross-Site Request Forgery vulnerability in the Web Profiler

## Summary
Severity: High
Advisory: GHSA-v35g-4rrw-h4fw
CVE: CVE-2014-6072
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-v35g-4rrw-h4fw
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/symfony` — affected >=2.5.0 <2.5.4
- Packagist: `symfony/web-profiler-bundle` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/web-profiler-bundle` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/web-profiler-bundle` — affected >=2.5.0 <2.5.4

## Details
All 2.0.X, 2.1.X, 2.2.X, 2.3.X, 2.4.X, and 2.5.X versions of the Symfony WebProfiler bundle are affected by this security issue.

This issue has been fixed in Symfony 2.3.19, 2.4.9, and 2.5.4. Note that no fixes are provided for Symfony 2.0, 2.1, and 2.2 as they are not maintained anymore.

### Description
The Symfony Web Profiler is a great development tool, but it should not be enabled on production servers. If it is enabled in production, it must be properly secured so that only authorized people have access to it. Developers must be very cautious about this as the Web Profiler gives many sensitive information about a Symfony project and any attackers can exploit many of them. Just to name a few sensitive information: user logins, user cookies, executed SQL statements, ...

That being said, the import/export feature of the web profiler is exploitable even if the Web Profiler is secured as the form to import a profiler is not protected against CSRF attacks. Combined with the fact that profiles are imported as a PHP serialized string, it makes your application vulnerable to code injection.

### Resolution
As the import/export feature of the Web Profiler is not that useful, and because PHP `serialize/unserialize` functions have a long history of vulnerabilities, I decided to remove this feature from the Web interface and move it as CLI commands.

If you were relying on this feature, you now need to use the `profiler:import` and `profiler:export` Symfony commands provided by the WebProfiler bundle from the command line interface.

Those commands are not enabled by default and must be activated explicitly. For Symfony 2.4+, you can import them in your `app/config.yml` configuration file:

 ```
import:
    - { resource: "%kernel.root_dir%/../vendor/symfony/symfony/src/Symfony/Bundle/WebProfilerBundle/Resources/config/commands.xml" }
```
For Symfony 2.3, you can use the following snippet of code in `app/console`:

```
$kernel = new AppKernel($env, $debug);
$application = new Application($kernel);
if ($kernel->getContainer()->has('profiler')) {
    $profiler = $kernel->getContainer()->get('profiler');
    $application->add(new ImportCommand($profiler));
    $application->add(new ExportCommand($profiler));
}
$application->run($input);
```
At this point, I want to reiterate that you should never enable the Symfony Web Profiler on your production servers as this is a development tool. And if you need to enable it, double-check that it is properly secured.

The patch for this issue is available here: https://github.com/symfony/symfony/pull/11832

## References
- https://github.com/symfony/symfony/pull/11832
- https://github.com/symfony/symfony/commit/f38536ab79058f6a934426c41170256ba9623a02
- https://github.com/symfony/web-profiler-bundle/commit/5b589ba83faf7eb20cec50725cd657075aebdd36
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2014-6072.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/web-profiler-bundle/CVE-2014-6072.yaml
- https://symfony.com/cve-2014-6072
