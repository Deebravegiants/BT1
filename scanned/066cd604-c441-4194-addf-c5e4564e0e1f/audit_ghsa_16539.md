# [M] Ez Platform and Legacy are prone to an insecure interpretation of PHP/PHAR uploads

## Summary
Severity: Medium
Advisory: GHSA-pqjm-xcp8-wgmm
CWE: CWE-94
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-pqjm-xcp8-wgmm
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2018.9.0 <2018.9.1.3
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2018.6.0 <2018.6.1.4
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2011.0.0 <2017.12.4.3
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.4.0 <5.4.12.3
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.3.0 <5.3.12.6

## Details
The eZ Platform and Legacy are affected by an issue related to how uploaded PHP and PHAR files are handled, and consists of two parts: 1. Web server configuration, and 2. Disabling the PHAR stream wrapper.

**1. WEB SERVER CONFIGURATION**
The sample web server configuration in our documentation can in some cases allow the execution of uploaded PHP/PHAR code. This can be abused to allow priviledge escalation and breach of content access controls, among other things. Please ensure that your web server will not execute files in directories were files may be uploaded, such as web/var/ and ezpublish_legacy/var/

As an example, here is how you can make Apache return HTTP 403 Forbidden for a number of executable file types in your eZ Platform var directory. Please adapt it to your needs. It is then possible to enable logging of HTTP 403 in a separate log file if you wish, you could do this to see if someone is trying to abuse the server.
```
RewriteEngine On

# disable .php(3) and other extensions in the var directory
RewriteRule ^var/.*(?i)\.(php3?|phar|phtml|sh|exe|pl|bin)$ - [F]
```
Here is the same configuration, but for the Nginx web server:
```
location ~ ^/var/.*(?i)\.(php3?|phar|phtml|sh|exe|pl|bin)$ {
  return 403;
}
```

**2. DISABLE PHAR STREAM WRAPPER**
PHAR archives may be crafted such that its stream wrapper will execute them without being specifically asked to. With such files, any PHP file operation may cause deserialisation and execution. This may happen even if the file name suffix isn't ".phar". Any site that allows file uploads is at risk. Normally eZ Platform has no need for PHAR support. It's only used by Composer, and that is executed separately from eZ Platform. So one way to avoid this vulnerability is to disable the PHAR stream wrapper within eZ Platform. (If you know you need PHAR support, please consider other means to deal with this vulnerability. For example, enabling the wrapper only in those scripts/bundles that have to deal with such files.)

Disabling the stream wrapper should be done in:

eZ Platform (web/app.php)
CLI scripts (bin/console)
Legacy (index.php and CLI scripts)

To install, use Composer to update to one of the "Resolving versions" mentioned above, or apply these patches manually:
https://github.com/ezsystems/ezplatform/commit/9a0c52dc4535e4b3ce379f80222dc53f705a2cfd
https://github.com/ezsystems/ezpublish-legacy/commit/d21957bf202b091ab39dfb5be300f6c30be3933e

## References
- https://github.com/ezsystems/ezplatform/commit/9a0c52dc4535e4b3ce379f80222dc53f705a2cfd
- https://github.com/ezsystems/ezpublish-legacy/commit/d21957bf202b091ab39dfb5be300f6c30be3933e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezpublish-legacy/2018-11-21-1.yaml
- https://github.com/ezsystems/ezpublish-legacy
- https://web.archive.org/web/20210614192208/https://share.ez.no/community-project/security-advisories/ezsa-2018-009-do-not-interpret-php-phar-uploads
- http://share.ez.no/community-project/security-advisories/ezsa-2018-009-do-not-interpret-php-phar-uploads
